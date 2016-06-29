# Flask-OpenTracing extension:

This extension allows for tracing of flask apps using the OpenTracing API. All
that it requires is for a FlaskTracing tracer to be initialized using an
instance of an OpenTracing tracer, and for any traced request functions to be
decorated with `@tracer.trace()`.

```python 
import opentracing
from flask_opentracing import FlaskTracer
app = Flask(__name__)

opentracing_tracer = ## some OpenTracing tracer implementation  
tracer = FlaskTracer(opentracing_tracer)

@app.route('/some_url') 
@tracer.trace(optional_args) 
def some_view_func():
	...     
	return some_view 
```

The OpenTracing tracer can be any implementation you choose. The optional
arguments for the tracer.trace() decorator are any number of attributes (as
strings) of flask.Request that you wish to set as tags on the created span.

If you wish to access a span for a request, you can call
`tracer.get_span(request)` for that request. If this is the current request,
this is `_request_ctx_stack.top.request`.

## Examples

See the examples folder to view and run an example of two Flask applications
with integrated OpenTracing tracers.
