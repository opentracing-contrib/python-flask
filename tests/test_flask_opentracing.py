import unittest

from flask import (Flask, request)
import opentracing
from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from flask_opentracing import FlaskTracing


app = Flask(__name__)
test_app = app.test_client()


empty_tracer = opentracing.Tracer()
tracing_all = FlaskTracing(MockTracer(), True, app, ['url'])
tracing = FlaskTracing(MockTracer())
tracing_deferred = FlaskTracing(lambda: MockTracer(),
                                True, app, ['url'])


def flush_spans(tcr):
    for req in tcr._current_spans:
        tcr._current_spans[req].finish()
    tcr._current_spans = {}


@app.route('/test')
def check_test_works():
    return 'Success'


@app.route('/another_test')
@tracing.trace('url', 'url_rule')
def decorated_fn():
    return 'Success again'


@app.route('/wire')
def send_request():
    span = tracing.get_span()
    headers = {}
    empty_tracer.inject(span, opentracing.Format.TEXT_MAP, headers)
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
            flush_spans(tracing_all)
            flush_spans(tracing_deferred)

    def test_span_deletion(self):
        assert not tracing_all._current_spans
        assert not tracing_deferred._current_spans
        test_app.get('/test')
        assert not tracing_all._current_spans
        assert not tracing_deferred._current_spans

    def test_span_tags(self):
        test_app.get('/test')

        spans = tracing_all._tracer.finished_spans()
        assert len(spans) == 1
        assert spans[0].tags == {
            tags.COMPONENT: 'Flask',
            tags.HTTP_METHOD: 'GET',
            tags.HTTP_STATUS_CODE: 200,
            tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
            tags.HTTP_URL: 'http://localhost/test',
            'url': 'http://localhost/test',  # extra tag
        }

    def test_requests_distinct(self):
        with app.test_request_context('/test'):
            app.preprocess_request()
        with app.test_request_context('/test'):
            app.preprocess_request()
            second_span = tracing_all._current_spans.pop(request)
            assert second_span
            second_span.finish()
            assert not tracing_all.get_span(request)
        # clear current spans
        flush_spans(tracing_all)
        flush_spans(tracing_deferred)

    def test_decorator(self):
        with app.test_request_context('/another_test'):
            app.preprocess_request()
            assert not tracing.get_span(request)
            assert len(tracing_deferred._current_spans) == 1
            assert len(tracing_all._current_spans) == 1
        flush_spans(tracing)
        flush_spans(tracing_all)
        flush_spans(tracing_deferred)

        test_app.get('/another_test')
        assert not tracing_all._current_spans
        assert not tracing._current_spans
        assert not tracing_deferred._current_spans

    def test_over_wire(self):
        rv = test_app.get('/wire')
        assert '200' in str(rv.status_code)
