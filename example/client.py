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

# could put this in an init_tracer method
ls_tracer = lightstep.tracer.init_tracer(group_name="example client", access_token="678ed8df5cb556751a4bfdfa51347666")
tracer = FlaskTracer(ls_tracer)

@app.route("/")
def index():
	return "Index Page"


@app.route("/request/<script>/<int:numrequests>")
@tracer.trace("url")
def send_multiple_requests(script, numrequests):
	'''
	Makes a request to the server
	Injects the current span into headers to continue trace
	'''
	span = tracer.get_span()
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

@app.route("/test")
@tracer.trace()
def test_lightstep_tracer():
	'''
	Simple function to ensure the tracer works.
	'''
	time.sleep(1)
	return "No errors"

