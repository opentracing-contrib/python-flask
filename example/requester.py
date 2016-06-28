import sys
sys.path.append("../")

from flask import (Flask, _request_ctx_stack as stack)
from flask_opentracing import FlaskTracer
import lightstep.tracer
import opentracing
import threading
import time
import urllib2

app = Flask(__name__)

## could put this in an init_tracer method
ls_tracer = lightstep.tracer.init_tracer(group_name="example requester", access_token="{your_lightstep_token}")
tracer = FlaskTracer(ls_tracer, False, ["send_request", "send_multiple_requests"], app)
tracer.trace_attributes("send_request", ["url", "url_rule", "method"])
tracer.trace_attributes("send_multiple_requests", ["url", "url_rule", "method"])

@app.route("/")
def index():
	return "Index Page"

## make a request to the responder
## injects the current span into headers to continue trace
@app.route("/request/<script>/<int:numrequests>")
def send_multiple_requests(script, numrequests):
	span = tracer.get_span(stack.top.request)
	def send_request():
		url = "http://localhost:5000/"+str(script)
		request = urllib2.Request(url)
		tracer.injectAsHeaders(span, request)
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError as ue:  
			response = ue
	for i in range(numrequests):
		send_request()
	return "Requests sent"

## just testing that the tracer works
@app.route("/test")
def test_lightstep_tracer():
	span = tracer.start_span("tracer test")
	time.sleep(1)
	span.finish()
	return "No errors"

