# Flask-OpenTracing extension:

This extension allows for tracing of flask apps using the OpenTracing API. All
that it requires is that the app initializes and configures the tracer when the
app starts. This can be done with the following code:

```python
opentracing_tracer = ## some OpenTracing tracer implementation 
tracer = FlaskTracer(opentracing_tracer, trace_all_requests=True, endpoints=[], app=None)
tracer.trace_attributes(endpoint, attributes) ## optional 
```

The OpenTracing tracer can be any implementation you choose. The FlaskTracer
parameters are the OpenTracing tracer to trace with, a boolean trace_all_requests
of whether you want to trace ALL incoming requests with a valid endpoint, a list
of endpoints that you wish to trace, and the app to trace (if left as `None`,
you can initialize it by calling `tracer.init_trace(app)`). The trace_attributes
function allows you to pass in an endpoint and list of request attributes that
you wish to record for that trace. For example, if you pass in the attribute
"url", then all spans for the given endpoint will log the its url for that
request instance.

If you wish to access a span for a request, you can call
`tracer.get_span(request)` for that request. If this is the current request,
this is `_request_ctx_stack.top.request`.

## Examples

See the examples folder to view and run an example of two Flask applications with
integrated OpenTracing tracers.
