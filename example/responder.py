import sys
sys.path.append("../")

from flask import (Flask, _request_ctx_stack as stack)
from flask_opentracing import FlaskTracer
import lightstep.tracer
import opentracing
import time
import urllib2

app = Flask(__name__)

## this method has to be before "tracer = " statement?
def init_tracer(app):
	ls_tracer = lightstep.tracer.init_tracer(group_name="example responder", access_token="{your_lightstep_token}")
	tracer = FlaskTracer(ls_tracer, False, ["simple_response", "create_child_span"], app)
	tracer.trace_attributes("create_child_span", ["url", "url_rule"])
	return tracer

tracer = init_tracer(app)

@app.route("/")
def index():
	return "Index Page"

## this request will be traced automatically
@app.route("/simple", methods=['GET'])
def simple_response():
	return "Hello, world!"

## this request will be traced automatically
## also demonstrates ability to get the request's span, log stuff,
## and create child spans to trace internal requests
@app.route("/childspan", methods=['GET'])
def create_child_span():
	current_request = stack.top.request
	parent_span = tracer.get_span(current_request)
	if parent_span is not None:
		child_span = tracer.start_span("inside create_child_span", parent_span)
	else:
		child_span = tracer.start_span("inside create_child_span")
	pows2 = calculate_some_stuff()
	child_span.finish()	
	return str(pows2)

def calculate_some_stuff():
	powers_of_two = []
	for i in range(10):
		power_of_two = 2**i
		powers_of_two.append(power_of_two)
	return powers_of_two




