import opentracing
from opentracing.ext import tags
from flask import _request_ctx_stack as stack


class FlaskTracing(opentracing.Tracer):
    """
    Tracer that can trace certain requests to a Flask app.

    @param tracer the OpenTracing tracer implementation to trace requests with
    """
    def __init__(self, tracer=None, trace_all_requests=False, app=None,
                 traced_attributes=[], start_span_cb=None):

        if start_span_cb is not None and not callable(start_span_cb):
            raise ValueError('start_span_cb is not callable')

        if not callable(tracer):
            self.__tracer = tracer
            self.__tracer_getter = None
        else:
            self.__tracer = None
            self.__tracer_getter = tracer

        self._trace_all_requests = trace_all_requests
        self._start_span_cb = start_span_cb
        self._current_spans = {}

        # tracing all requests requires that app != None
        if self._trace_all_requests:
            @app.before_request
            def start_trace():
                self._before_request_fn(traced_attributes)

            @app.after_request
            def end_trace(response):
                self._after_request_fn(response)
                return response

    @property
    def _tracer(self):
        """DEPRECATED"""
        return self.tracer

    @property
    def tracer(self):
        if not self.__tracer:
            if self.__tracer_getter is None:
                return opentracing.tracer

            self.__tracer = self.__tracer_getter()

        return self.__tracer

    def trace(self, *attributes):
        """
        Function decorator that traces functions

        NOTE: Must be placed after the @app.route decorator

        @param attributes any number of flask.Request attributes
        (strings) to be set as tags on the created span
        """
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
        """
        Returns the span tracing `request`, or the current request if
        `request==None`.

        If there is no such span, get_span returns None.

        @param request the request to get the span from
        """
        if request is None and stack.top:
            request = stack.top.request
        return self._current_spans.get(request, None)

    def _before_request_fn(self, attributes):
        request = stack.top.request
        operation_name = request.endpoint
        headers = {}
        for k, v in request.headers:
            headers[k.lower()] = v
        span = None
        try:
            span_ctx = self.tracer.extract(opentracing.Format.HTTP_HEADERS,
                                           headers)
            span = self.tracer.start_span(operation_name=operation_name,
                                          child_of=span_ctx)
        except (opentracing.InvalidCarrierException,
                opentracing.SpanContextCorruptedException):
            span = self.tracer.start_span(operation_name=operation_name)

        self._current_spans[request] = span

        span.set_tag(tags.COMPONENT, 'Flask')
        span.set_tag(tags.HTTP_METHOD, request.method)
        span.set_tag(tags.HTTP_URL, request.base_url)
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)

        for attr in attributes:
            if hasattr(request, attr):
                payload = str(getattr(request, attr))
                if payload:
                    span.set_tag(attr, payload)

        self._call_start_span_cb(span, request)

    def _after_request_fn(self, response=None):
        request = stack.top.request

        # the pop call can fail if the request is interrupted by a
        # `before_request` method so we need a default
        span = self._current_spans.pop(request, None)
        if span is not None:
            if response is not None:
                span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)

            span.finish()

    def _call_start_span_cb(self, span, request):
        if self._start_span_cb is None:
            return

        try:
            self._start_span_cb(span, request)
        except Exception:
            pass
