import sys
sys.path.append("../")

from flask import (Flask, _request_ctx_stack as stack)
from flask_opentracing import FlaskTracer
import lightstep.tracer
import opentracing
import time
import urllib2

app = Flask(__name__)
ls_tracer = lightstep.tracer.init_tracer(group_name="example server", access_token="{your_lightstep_token}")
tracer = FlaskTracer(ls_tracer)

@app.route("/")
def index():
	return "Index Page"

@app.route("/simple", methods=['GET'])
@tracer.trace("url")
def simple_response():
	'''
	This request will be automatically traced.
	'''
	return "Hello, world!"

@app.route("/childspan", methods=['GET'])
@tracer.trace("headers")
def create_child_span():
	'''
	This request will also be automatically traced.
	
	This is a more complicated example of accessing the current 
	request from within a handler and creating new spans manually.
	'''
	current_request = stack.top.request
	parent_span = tracer.get_span(current_request)
	if parent_span is not None:
		child_span = ls_tracer.start_span("inside create_child_span", parent_span)
	else:
		child_span = ls_tracer.start_span("inside create_child_span")
	ans = calculate_some_stuff()
	child_span.finish()	
	return str(ans)

def calculate_some_stuff():
	two = 1 + 1
	return two




