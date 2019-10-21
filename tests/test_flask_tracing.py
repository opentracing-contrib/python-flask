import mock
import unittest

from flask import (Flask, request)
import opentracing
from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from flask_opentracing import FlaskTracing


app = Flask(__name__)
test_app = app.test_client()


tracing_all = FlaskTracing(MockTracer(), True, app, ['url'])
tracing = FlaskTracing(MockTracer())
tracing_deferred = FlaskTracing(lambda: MockTracer(),
                                True, app, ['url'])


def flush_spans(tcr):
    for req in tcr._current_scopes:
        tcr._current_scopes[req].close()
    tcr._current_scopes = {}


@app.route('/test')
def check_test_works():
    return 'Success'


@app.route('/another_test')
@tracing.trace('url', 'url_rule')
def decorated_fn():
    return 'Success again'


@app.route('/another_test_simple')
@tracing.trace('query_string', 'is_xhr')
def decorated_fn_simple():
    return 'Success again'


@app.route('/error_test')
@tracing.trace()
def decorated_fn_with_error():
    raise RuntimeError('Should not happen')


@app.route('/decorated_child_span_test')
@tracing.trace()
def decorated_fn_with_child_span():
    with tracing.tracer.start_active_span('child'):
        return 'Success'


@app.route('/wire')
def send_request():
    span = tracing_all.get_span()
    headers = {}
    tracing_all.tracer.inject(span.context,
                              opentracing.Format.TEXT_MAP,
                              headers)
    rv = test_app.get('/test', headers=headers)
    return str(rv.status_code)


class TestTracing(unittest.TestCase):
    def setUp(self):
        tracing_all._tracer.reset()
        tracing._tracer.reset()
        tracing_deferred._tracer.reset()

    def test_span_creation(self):
        with app.test_request_context('/test'):
            app.preprocess_request()
            assert tracing_all.get_span(request)
            assert not tracing.get_span(request)
            assert tracing_deferred.get_span(request)

            active_span = tracing_all.tracer.active_span
            assert tracing_all.get_span(request) is active_span

            flush_spans(tracing_all)
            flush_spans(tracing_deferred)

    def test_span_deletion(self):
        assert not tracing_all._current_scopes
        assert not tracing_deferred._current_scopes
        test_app.get('/test')
        assert not tracing_all._current_scopes
        assert not tracing_deferred._current_scopes

    def test_span_tags(self):
        test_app.get('/another_test_simple')

        spans = tracing._tracer.finished_spans()
        assert len(spans) == 1
        assert spans[0].tags == {
            tags.COMPONENT: 'Flask',
            tags.HTTP_METHOD: 'GET',
            tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
            tags.HTTP_URL: 'http://localhost/another_test_simple',
            'is_xhr': 'False',
        }

    def test_requests_distinct(self):
        with app.test_request_context('/test'):
            app.preprocess_request()
        with app.test_request_context('/test'):
            app.preprocess_request()
            second_scope = tracing_all._current_scopes.pop(request)
            assert second_scope
            second_scope.close()
            assert not tracing_all.get_span(request)
        # clear current spans
        flush_spans(tracing_all)
        flush_spans(tracing_deferred)

    def test_decorator(self):
        with app.test_request_context('/another_test'):
            app.preprocess_request()
            assert not tracing.get_span(request)
            assert len(tracing_deferred._current_scopes) == 1
            assert len(tracing_all._current_scopes) == 1

            active_span = tracing_all.tracer.active_span
            assert tracing_all.get_span(request) is active_span

        flush_spans(tracing)
        flush_spans(tracing_all)
        flush_spans(tracing_deferred)

        test_app.get('/another_test')
        assert not tracing_all._current_scopes
        assert not tracing._current_scopes
        assert not tracing_deferred._current_scopes

    def test_decorator_trace_all(self):
        # Fake we are tracing all, which should disable
        # tracing through our decorator.
        with mock.patch.object(tracing, '_trace_all_requests', new=True):
            rv = test_app.get('/another_test_simple')
            assert '200' in str(rv.status_code)

        spans = tracing.tracer.finished_spans()
        assert len(spans) == 0

    def test_error(self):
        try:
            test_app.get('/error_test')
        except RuntimeError:
            pass

        assert len(tracing._current_scopes) == 0
        assert len(tracing_all._current_scopes) == 0
        assert len(tracing_deferred._current_scopes) == 0

        # Registered handler.
        spans = tracing.tracer.finished_spans()
        assert len(spans) == 1
        self._verify_error(spans[0])

        # Decorator.
        spans = tracing.tracer.finished_spans()
        assert len(spans) == 1
        self._verify_error(spans[0])

    def _verify_error(self, span):
        assert span.tags.get(tags.ERROR) is True

        assert len(span.logs) == 1
        assert span.logs[0].key_values.get('event', None) is tags.ERROR
        assert isinstance(
                span.logs[0].key_values.get('error.object', None),
                RuntimeError
        )

    def test_over_wire(self):
        rv = test_app.get('/wire')
        assert '200' in str(rv.status_code)

        spans = tracing_all.tracer.finished_spans()
        assert len(spans) == 2
        assert spans[0].context.trace_id == spans[1].context.trace_id
        assert spans[0].parent_id == spans[1].context.span_id

    def test_child_span(self):
        rv = test_app.get('/decorated_child_span_test')
        assert '200' in str(rv.status_code)

        spans = tracing.tracer.finished_spans()
        assert len(spans) == 2
        assert spans[0].context.trace_id == spans[1].context.trace_id
        assert spans[0].parent_id == spans[1].context.span_id


class TestTracingStartSpanCallback(unittest.TestCase):
    def test_simple(self):
        def start_span_cb(span, request):
            span.set_tag('component', 'not-flask')
            span.set_tag('mytag', 'myvalue')

        tracing = FlaskTracing(MockTracer(), True, app,
                               start_span_cb=start_span_cb)
        rv = test_app.get('/test')
        assert '200' in str(rv.status_code)

        spans = tracing.tracer.finished_spans()
        assert len(spans) == 1
        assert spans[0].tags.get(tags.COMPONENT, None) == 'not-flask'
        assert spans[0].tags.get('mytag', None) == 'myvalue'

    def test_error(self):
        def start_span_cb(span, request):
            raise RuntimeError('Should not happen')

        tracing = FlaskTracing(MockTracer(), True, app,
                               start_span_cb=start_span_cb)
        rv = test_app.get('/test')
        assert '200' in str(rv.status_code)

        spans = tracing.tracer.finished_spans()
        assert len(spans) == 1
        assert spans[0].tags.get(tags.ERROR, None) is None
