from flask import (Flask, request)
import opentracing
import sys
sys.path.append('../')
from flask_opentracing import FlaskTracer
import copy

app = Flask(__name__)
test_app = app.test_client()

empty_tracer = opentracing.Tracer()
tracer_with_attributes = FlaskTracer(empty_tracer, True, app, ['url', 'url_rule'])
tracer_without_attributes = FlaskTracer(empty_tracer, True, app)
tracer = FlaskTracer(empty_tracer)

@app.route('/test')
def check_test_works():
    return "Success"

@app.route('/another_test')
def check_two_tests_work():
    return "Success again"

def test_on():
    assert True

def test_span_creation():
    with app.test_request_context('/test'):
        app.preprocess_request()
        assert tracer_with_attributes.get_span(request)
        assert tracer_without_attributes.get_span(request)
        # clear current spans
        span = tracer_with_attributes.get_span(request)
        span2 = tracer_with_attributes.get_span(request)
        span.finish()
        span2.finish()
        tracer_with_attributes._current_spans = {}
        tracer_without_attributes._current_spans = {}

def test_span_deletion():
    assert not tracer_with_attributes._current_spans
    assert not tracer_without_attributes._current_spans
    test_app.get('/test')
    assert not tracer_with_attributes._current_spans
    assert not tracer_without_attributes._current_spans

def test_requests_distinct():
    with app.test_request_context('/test'):
        app.preprocess_request()
    with app.test_request_context('/test'):
        app.preprocess_request()
        span = tracer_with_attributes._current_spans.pop(request)
        span2 = tracer_without_attributes._current_spans.pop(request)
        assert span
        assert span2
        span.finish()
        span2.finish()
        assert not tracer_with_attributes.get_span(request)
        assert not tracer_without_attributes.get_span(request)
    # clear current spans
    for req in tracer_with_attributes._current_spans:
        tracer_with_attributes._current_spans[req].finish()
    tracer_with_attributes._current_spans = {}    
    for req in tracer_without_attributes._current_spans:
        tracer_without_attributes._current_spans[req].finish()
    tracer_without_attributes._current_spans = {}

# TODO: Tests for inject/extract; wait until new opentracing is on pypi