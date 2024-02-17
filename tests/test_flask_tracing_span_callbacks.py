import unittest
from abc import abstractmethod

from flask import Flask
from opentracing.ext import tags
from opentracing.mocktracer import MockTracer
from flask_opentracing import FlaskTracing


class _StartSpanCallbackTestCase(unittest.TestCase):
    @staticmethod
    @abstractmethod
    def start_span_cb(span, request):
        pass

    def setUp(self):
        self.app = Flask(__name__)
        self.tracing = FlaskTracing(
            MockTracer(), True, self.app, start_span_cb=self.start_span_cb
        )
        self.test_app = self.app.test_client()

        @self.app.route('/test')
        def check_test_works():
            return 'Success'


class TestFlaskTracingStartSpanCallbackSetTags(_StartSpanCallbackTestCase):
    @staticmethod
    def start_span_cb(span, request):
        print('setting tags')
        span.set_tag('component', 'not-flask')
        span.set_tag('mytag', 'myvalue')

    def test_simple(self):
        rv = self.test_app.get('/test')
        assert '200' in str(rv.status_code)

        spans = self.tracing.tracer.finished_spans()
        assert len(spans) == 1
        assert spans[0].tags.get(tags.COMPONENT, None) == 'not-flask'
        assert spans[0].tags.get('mytag', None) == 'myvalue'


class TestFlaskTracingStartSpanCallbackRaisesError(
    _StartSpanCallbackTestCase
):
    @staticmethod
    def start_span_cb(span, request):
        print('raising exception')
        raise RuntimeError('Should not happen')

    def test_error(self):
        rv = self.test_app.get('/test')
        assert '200' in str(rv.status_code)

        spans = self.tracing.tracer.finished_spans()
        assert len(spans) == 1
        assert spans[0].tags.get(tags.ERROR, None) is None
