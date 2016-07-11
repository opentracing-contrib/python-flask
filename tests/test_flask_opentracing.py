from flask import (Flask, request)
import opentracing
from flask_opentracing import FlaskTracer

app = Flask(__name__)
test_app = app.test_client()

empty_tracer = opentracing.Tracer()
tracer_all = FlaskTracer(empty_tracer, True, app, ['url'])
tracer = FlaskTracer(empty_tracer)

def flush_spans(tcr):
    for req in tcr._current_spans:
        tcr._current_spans[req].finish()
    tcr._current_spans = {}

@app.route('/test')
def check_test_works():
    return "Success"

@app.route('/another_test')
@tracer.trace('url', 'url_rule')
def decorated_fn():
    return "Success again"

@app.route('/wire')
def send_request():
    span = tracer.get_span()
    headers = {}
    empty_tracer.inject(span, opentracing.Format.TEXT_MAP, headers)   
    rv = test_app.get('/test', headers=headers)
    return str(rv.status_code)

def test_on():
    assert True

def test_span_creation():
    with app.test_request_context('/test'):
        app.preprocess_request()
        assert tracer_all.get_span(request)
        assert not tracer.get_span(request)
        flush_spans(tracer_all)

def test_span_deletion():
    assert not tracer_all._current_spans
    test_app.get('/test')
    assert not tracer_all._current_spans

def test_requests_distinct():
    with app.test_request_context('/test'):
        app.preprocess_request()
    with app.test_request_context('/test'):
        app.preprocess_request()
        second_span = tracer_all._current_spans.pop(request)
        assert second_span
        second_span.finish()
        assert not tracer_all.get_span(request)
    # clear current spans
    flush_spans(tracer_all)

def test_decorator():
    with app.test_request_context('/another_test'):
        app.preprocess_request()
        assert not tracer.get_span(request)
        assert len(tracer_all._current_spans) == 1
    flush_spans(tracer)
    flush_spans(tracer_all)

    test_app.get('/another_test')
    assert not tracer_all._current_spans
    assert not tracer._current_spans

def test_over_wire():
    rv = test_app.get('/wire')
    assert '200' in rv.data

