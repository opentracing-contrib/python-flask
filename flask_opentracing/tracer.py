import opentracing
from flask import (Request, _request_ctx_stack as stack)

class FlaskTracer(opentracing.Tracer):
    '''
    Tracer that can trace certain requests to a Flask app.

    @param tracer the OpenTracing tracer implementation to trace requests with
    '''
    def __init__(self, tracer, trace_all_requests=False, app=None, traced_attributes=[]): 
        self._tracer = tracer
        self._trace_all_requests = trace_all_requests
        self._current_spans = {}
        self._trace_all_requests = trace_all_requests

        # tracing all requests requires that app != None
        if self._trace_all_requests:
            @app.before_request
            def start_trace():
                self._before_request_fn(traced_attributes)

            @app.after_request
            def end_trace(response):
                self._after_request_fn()
                return response


    def trace(self, *attributes):
        '''
        Function decorator that traces functions
        NOTE: Must be placed after the @app.route decorator

        @param attributes any number of flask.Request attributes
        (strings) to be set as tags on the created span
        '''
        def decorator(f):
            def wrapper(*args, **kwargs):
                if not self._trace_all_requests:
                    self._before_request_fn(list(attributes))
                    r = f(*args, **kwargs)
                    self._after_request_fn()
                    return r
                else:
                    return f(*args, **kwargs)
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

    def _before_request_fn(self, attributes):
        request = stack.top.request
        operation_name = request.endpoint
        headers = {}
        for k,v in request.headers:
            headers[k.lower()] = v
        span = None
        try:
            span_ctx = self._tracer.extract(opentracing.Format.TEXT_MAP, headers)
            span = self._tracer.start_span(operation_name=operation_name, references=opentracing.ChildOf(span_ctx))
        except (opentracing.InvalidCarrierException, opentracing.SpanContextCorruptedException) as e:
            span = self._tracer.start_span(operation_name=operation_name, tags={"Extract failed": str(e)})
        if span is None:
            span = self._tracer.start_span(operation_name)
        self._current_spans[request] = span
        for attr in attributes:
            if hasattr(request, attr):
                payload = str(getattr(request, attr))
                if payload:
                    span.set_tag(attr, payload)

    def _after_request_fn(self):
        request = stack.top.request
        span = self._current_spans.pop(request)
        span.finish()

