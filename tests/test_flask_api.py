import mock
import unittest

import opentracing
from flask_opentracing import FlaskTracing


class TestValues(unittest.TestCase):
    def test_tracer(self):
        tracer = opentracing.Tracer()
        tracing = FlaskTracing(tracer)
        assert tracing.tracer is tracer
        assert tracing.tracer is tracing._tracer

    def test_global_tracer(self):
        tracing = FlaskTracing()
        with mock.patch('opentracing.tracer'):
            assert tracing.tracer is opentracing.tracer
            opentracing.tracer = object()
            assert tracing.tracer is opentracing.tracer
