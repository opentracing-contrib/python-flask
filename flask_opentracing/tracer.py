import opentracing
import time
from flask import (Request, _request_ctx_stack as stack)

class FlaskTracer(opentracing.Tracer):
	'''
	Tracer that can trace certain requests to a Flask app.

	@param tracer the OpenTracing tracer implementation to trace requests with
	'''
	def __init__(self, tracer, trace_all_requests=False): 
		self._tracer = tracer
		self._trace_all_requests = trace_all_requests
		self._current_spans = {}

	def trace(self, *attributes):
		'''
		Function decorator that traces functions
		NOTE: Must be placed after the @app.route decorator

		@param attributes any number of flask.Request attributes
		(strings) to be set as tags on the created span
		'''
		def decorator(f):
			def wrapper(*args, **kwargs):
				request = stack.top.request
				operation_name = request.endpoint
				headers = {}
				for k,v in request.headers:
					headers[k.lower()] = v
				span = None
				try:
					span = self._tracer.join(operation_name, opentracing.Format.TEXT_MAP, headers)
				except:
					span = self._tracer.start_span(operation_name)
				self._current_spans[request] = span
				for attr in attributes:
					if hasattr(request, attr):
						payload = str(getattr(request, attr))
						if payload is not "":
							span.set_tag(attr, payload)

				r = f(*args, **kwargs)

				span.finish()
				self._current_spans.pop(request)
				return r
			wrapper.__name__ = f.__name__
			return wrapper
		return decorator

	def get_span(self, request=None):
		'''
		Returns the span tracing the current request, or the given
		If the request doesn't exist then returns None.

		@param request the request to get the span from
		'''
		if request is None:
			request = stack.top.request
		return self._current_spans.get(request, None)

	def inject_as_headers(self, span, request):
		text_carrier = {}
		self._tracer.inject(span, opentracing.Format.TEXT_MAP, text_carrier)
		for k, v in text_carrier.iteritems():
			request.add_header(k,v)
