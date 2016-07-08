from flask import (Flask, request)
import opentracing
import sys
sys.path.append('../')
from flask_opentracing import FlaskTracer
import copy

app = Flask(__name__)
test_app = app.test_client()

empty_tracer = opentracing.Tracer()
tracer = FlaskTracer(empty_tracer, True, app, ['url', 'url_rule'])
tracer_without_attributes = FlaskTracer(empty_tracer, True, app)

print "HI"
assert True 

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
        assert tracer.get_span(request)
        # clear current spans
        span = tracer.get_span(request)
        span.finish()
        tracer._current_spans = {}

def test_span_deletion():
    assert not tracer._current_spans
    test_app.get('/test')
    assert not tracer._current_spans

def test_spans_unique():
    with app.test_request_context('/test'):
        app.preprocess_request()
    with app.test_request_context('/another_test'):
        app.preprocess_request()
        second_span = tracer.get_span(request)
        assert tracer.get_span(request) == second_span
        second_span = tracer._current_spans.pop(request)
        second_span.finish()
        assert not tracer.get_span(request)
        for req in tracer._current_spans:
            tracer._current_spans[req].finish()
    tracer._current_spans = {}