import opentracing
import time
from flask import (Request, _request_ctx_stack as stack)

class FlaskTracer(opentracing.Tracer):
	'''
	Tracer that can trace certain requests to a Flask app.

	@param tracer the OpenTracing tracer implementation to trace requests with
	@param trace_all_requests whether to trace all requests to the app
	@param traced_funcs the names of the functions to trace, if not
		tracing all requests
	@param app the app to bind this tracer to (can be set later)
	'''
	def __init__(self, tracer, trace_all_requests=True, traced_funcs=[], app=None): 
		self._tracer = tracer
		self._trace_all_requests = trace_all_requests
		self._traced_funcs = traced_funcs
		self._current_spans = {}
		self._traced_attributes = {}
		self._valid_attributes = self._get_valid_attributes()
		# self.on = true
		if app != None:
			self.init_trace(app)

	def init_trace(self, app):
		'''
		Initializes tracing on the given app.
		'''
		@app.before_request
		def create_span():
			# if self.on:
			request = stack.top.request
			operation_name = request.endpoint
			if(self._trace_all_requests or operation_name in self._traced_funcs):	
				print "tracing " + str(operation_name)	

				## Can get rid of this once the python tracer is updated
				headers = {}
				for k, v in request.headers:
					headers[k.lower()] = v
				
				span = None
				
				try:
					span = self._tracer.join(operation_name, opentracing.Format.TEXT_MAP, headers)
				except:
					span = self._tracer.start_span(operation_name)

				for attr in self._traced_attributes.get(operation_name, []):
					try:
						payload = str(getattr(request, attr))
						if payload is not "":
							span.set_tag(attr, payload)
					except:
						span.set_tag("Error: Attribute does not exist", str(attr))

				self._current_spans[request] = span

		@app.after_request
		def end_span(response):
			request = stack.top.request
			span = self._current_spans.get(request, False)
			if(span):
				print "ending span: " + str(request.endpoint)
				span.finish()
			return response

	def get_span(self, request, new_span_name=None):
		'''
		Returns the span tracing this request, if it exists.
		If it doesn't exist then returns None, or if new_span_name 
		is passed in, a new span with operation name new_span_name.

		@param request the request to find the trace of 
		@param new_span_name optional argument that, if a span is
			not found, is the operation name for a newly created span
		'''
		span = self._current_spans.get(request, None)
		if span is None and new_span_name is not None:
			span = tracer.start_span(new_span_name)
		return span

	def trace_funcs(endpoints):
		'''
		@param endpoints list of endpoints to trace
		'''
		for endpoint in endpoints:
			if endpoint not in self._traced_funcs:
				self._traced_funcs += endpoint

	def untrace_funcs(endpoints):
		'''
		@param endpoints list of endpoints to stop tracing if 
			they're currently being traced
		'''
		for endpoint in endpoints:
			if endpoint in self._traced_funcs:
				self._traced_funcs -= endpoint

	def trace_all_requests(boolean):
		'''
		@param whether to trace all requests
		'''
		self._trace_all_requests = boolean

	def trace_attributes(self, endpoint, attributes):
		'''
		@param endpoint the endpoint to set traced attributes for
		@param attributes a list of flask.Request attributes that 
			you wish to trace for the endpoint
		'''
		for attribute in attributes:
			if attribute in self._valid_attributes:
				if self._traced_attributes.get(endpoint, False):
					self._traced_attributes[endpoint].append(attribute)
				else:
					self._traced_attributes[endpoint] = [attribute]
			else:
				raise AttributeError("Attribute " + str(attribute) + " does not exist for flask.Request")

	def _get_valid_attributes(self):
		attributes = {'args', 'values', 'cookies', 
			'data', 'files', 'environ', 'method', 'path', 'full_path', 
			'script_root', 'base_url', 'url', 'url_root', 'is_xhr', 
			'get_json', 'on_json_loading_failed', 'url_rule', 'view_args' }
		return attributes
		## forms, headers, blueprint, max_content_length, module, routing_exception

	def start_span(self, operation_name=None, parent=None, tags=None, start_time=None):
		return self._tracer.start_span(operation_name, parent, tags, start_time)

	def inject(self, span, format, carrier):
		return self._tracer.inject(span, format, carrier)

	def injectAsHeaders(self, span, request):
		text_carrier = {}
		self._tracer.inject(span, opentracing.Format.TEXT_MAP, text_carrier)
		for k, v in text_carrier.iteritems():
			request.add_header(k,v)

	def join(self, operation_name, format, carrier):
		return self._tracer.join(operation_name, format, carrier)

	def flush(self):
		return self._tracer.flush()

	## (Incomplete) Additional methods in case multiple tracers 
	## are being used, and there is a need for turning on/off tracers 
	## while the app is running. Not sure whether this is necessary.
	
	# def is_on(): 
	# 	return self.on

	# def turn_on():
	# 	self.on = True

	# def turn_off():
	# 	self.on = False

# def set_tracer(tracer):
# 	ctx = stack.top
# 	# if hasattr(ctx, 'tracer'):
# 	# 	old_tracer = getattr(ctx, 'tracer')
# 	# 	old_tracer.turn_off()
# 	ctx.tracer = tracer
# 	tracer.trace_requests(current_app)

# def get_tracer():
# 	ctx = stack.top
# 	if hasattr(ctx, 'tracer'):
# 		tracer = getattr(ctx, 'tracer')
# 		return tracer
# 	else:
# 		return None
