import sys
sys.path.append("../")

from flask import Flask
from flask_opentracing import FlaskTracer
import lightstep.tracer
import opentracing
import urllib2

app = Flask(__name__)

# one-time tracer initialization code
ls_tracer = lightstep.tracer.init_tracer(group_name="example client", access_token="{your_lightstep_token}")
# this tracer does not trace all requests, so the @tracer.trace() decorator must be used
tracer = FlaskTracer(ls_tracer)

@app.route("/")
def index():
	'''
	Index page, has no tracing.
	'''
	return "Index Page"


@app.route("/request/<script>/<int:numrequests>")
@tracer.trace("url")
def send_multiple_requests(script, numrequests):
	'''
	Traced function that makes a request to the server
	Injects the current span into headers to continue trace
	'''
	span = tracer.get_span()
	def send_request():
		url = "http://localhost:5000/"+str(script)
		request = urllib2.Request(url)
		inject_as_headers(ls_tracer, span, request)
		try:
			response = urllib2.urlopen(request)
		except urllib2.URLError as ue:  
			response = ue
	for i in range(numrequests):
		send_request()
	return "Requests sent"

@app.route('/log')
@tracer.trace()
def log_something():
	'''
	Traced function that logs something to the current 
	request span.
	'''
	span = tracer.get_span()
	span.log_event("hello world")
	return "Something was logged"

@app.route("/test")
@tracer.trace()
def test_lightstep_tracer():
	'''
	Simple traced function to ensure the tracer works.
	'''
	return "No errors"

def inject_as_headers(tracer, span, request):
    text_carrier = {}
    tracer.inject(span, opentracing.Format.TEXT_MAP, text_carrier)
    for k, v in text_carrier.iteritems():
        request.add_header(k,v)

