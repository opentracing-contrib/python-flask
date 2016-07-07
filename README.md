# Flask-OpenTracing extension:

This extension allows for tracing of flask apps using the OpenTracing API. All
that it requires is for a FlaskTracing tracer to be initialized using an
instance of an OpenTracing tracer. You can either trace all requests to your site, or use function decorators to trace certain individual requests.

### Trace All Requests

```python
import opentracing
from flask_opentracing import FlaskTracer

app = Flask(__name__)

opentracing_tracer = ## some OpenTracing tracer implementation
tracer = FlaskTracer(opentracing_tracer, True, app, [optional_args])
```

### Trace Individual Requests

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

### Notes
The OpenTracing tracer can be any implementation you choose. In both cases, the optional
arguments are any number of attributes (as strings) of `flask.Request` that you wish to set as tags on the created span.

If you wish to access the span for the current request, you can call
`tracer.get_span()`. If you wish to access the span for a different active
request, you can call `tracer.get_span(request)` for that request.

## Examples

See the examples folder to view and run an example of two Flask applications
with integrated OpenTracing tracers.
