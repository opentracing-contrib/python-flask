import opentracing
from opentracing.ext import tags
from flask import _request_ctx_stack as stack

from .scope_manager import FlaskScopeManager


class FlaskTracing(opentracing.Tracer):
    """
    Tracer that can trace certain requests to a Flask app.

    @param tracer the OpenTracing tracer implementation to trace requests with
    """
    def __init__(self, tracer=None, trace_all_requests=None, app=None,
                 traced_attributes=[], start_span_cb=None):

        if start_span_cb is not None and not callable(start_span_cb):
            raise ValueError('start_span_cb is not callable')

        if trace_all_requests is True and app is None:
            raise ValueError('trace_all_requests=True requires an app object')

        if trace_all_requests is None:
            trace_all_requests = False if app is None else True

        if not callable(tracer):
            self.__tracer = tracer
            self.__tracer_getter = None
        else:
            self.__tracer = None
            self.__tracer_getter = tracer

        self._trace_all_requests = trace_all_requests
        self._start_span_cb = start_span_cb
        self._current_scopes = {}

        # tracing all requests requires that app != None
        if self._trace_all_requests:
            @app.before_request
            def start_trace():
                self._before_request_fn(traced_attributes)

            @app.after_request
            def end_trace(response):
                self._after_request_fn(response)
                return response

            @app.teardown_request
            def end_trace_with_error(error):
                if error is not None:
                    self._after_request_fn(error=error)

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
                if self._trace_all_requests:
                    return f(*args, **kwargs)

                self._before_request_fn(list(attributes))
                try:
                    r = f(*args, **kwargs)
                except Exception as e:
                    self._after_request_fn(error=e)
                    raise

                self._after_request_fn()
                return r

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

        scope = self._current_scopes.get(request, None)
        return None if scope is None else scope.span

    def _before_request_fn(self, attributes):
        request = stack.top.request
        operation_name = request.endpoint
        headers = {}
        for k, v in request.headers:
            headers[k.lower()] = v

        try:
            span_ctx = self.tracer.extract(opentracing.Format.HTTP_HEADERS,
                                           headers)
            scope = self.tracer.start_active_span(operation_name,
                                                  child_of=span_ctx)
        except (opentracing.InvalidCarrierException,
                opentracing.SpanContextCorruptedException):
            scope = self.tracer.start_active_span(operation_name)

        self._current_scopes[request] = scope

        span = scope.span
        span.set_tag(tags.COMPONENT, 'Flask')
        span.set_tag(tags.HTTP_METHOD, request.method)
        span.set_tag(tags.HTTP_URL, request.base_url)
        span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)

        for attr in attributes:
            if hasattr(request, attr):
                payload = getattr(request, attr)
                if payload not in ('', b''):  # python3
                    span.set_tag(attr, str(payload))

        self._call_start_span_cb(span, request)

    def _after_request_fn(self, response=None, error=None):
        # the pop call can fail if the request is interrupted by a
        # `before_request` method so we need a default
        scope = self._current_scopes.pop(stack.top.request, None)

        if isinstance(self.tracer.scope_manager, FlaskScopeManager):
            scope = self.tracer.scope_manager.active
        if scope is None:
            return

        if response is not None:
            scope.span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
        if error is not None:
            scope.span.set_tag(tags.ERROR, True)
            scope.span.set_tag('sfx.error.message', str(error))
            scope.span.set_tag('sfx.error.object', str(error.__class__))
            scope.span.set_tag('sfx.error.kind', error.__class__.__name__)

        scope.close()

    def _call_start_span_cb(self, span, request):
        if self._start_span_cb is None:
            return

        try:
            self._start_span_cb(span, request)
        except Exception:
            pass
