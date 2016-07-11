from flask import Flask
from flask_opentracing import FlaskTracer
import lightstep.tracer
import opentracing
import urllib2

app = Flask(__name__)

# one-time tracer initialization code
ls_tracer = lightstep.tracer.init_tracer(group_name="example server", access_token="{your_lightstep_token}")
# This tracer traces all requests
tracer = FlaskTracer(ls_tracer, True, app, ["url_rule"])

@app.route("/simple")
def simple_response():
	'''
	This request will be automatically traced.
	'''
	return "Hello, world!"

@app.route("/childspan")
def create_child_span():
	'''
	This request will also be automatically traced.
	
	This is a more complicated example of accessing the current 
	request from within a handler and creating new spans manually.
	'''
	parent_span = tracer.get_span()
	child_span = ls_tracer.start_span("inside create_child_span", opentracing.ChildOf(parent_span.context))
	ans = calculate_some_stuff()
	child_span.finish()	
	return str(ans)

def calculate_some_stuff():
	two = 1 + 1
	return two




