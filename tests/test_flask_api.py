import mock
import pytest
import unittest

import opentracing
from flask import Flask
from flask_opentracing import FlaskTracing


class TestValues(unittest.TestCase):
    def test_tracer(self):
        tracer = opentracing.Tracer()
        tracing = FlaskTracing(tracer)
        assert tracing.tracer is tracer
        assert tracing.tracer is tracing._tracer
        assert tracing._trace_all_requests is False

    def test_global_tracer(self):
        tracing = FlaskTracing()
        with mock.patch('opentracing.tracer'):
            assert tracing.tracer is opentracing.tracer
            opentracing.tracer = object()
            assert tracing.tracer is opentracing.tracer

    def test_trace_all_requests(self):
        app = Flask('dummy_app')
        tracing = FlaskTracing(app=app)
        assert tracing._trace_all_requests is True

        tracing = FlaskTracing(app=app, trace_all_requests=False)
        assert tracing._trace_all_requests is False

    def test_trace_all_requests_no_app(self):
        # when trace_all_requests is True, an app object is *required*
        with pytest.raises(ValueError):
            FlaskTracing(trace_all_requests=True)

    def test_start_span_invalid(self):
        with pytest.raises(ValueError):
            FlaskTracing(start_span_cb=0)
