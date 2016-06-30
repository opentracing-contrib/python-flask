## Example

This example has a flask client and server and shows they can trace requests
both within and between the two sites using the flask_opentracing extension and
a concrete variant of an OpenTracing tracer. To run, make sure that you run pip
install for flask, opentracing, and lightstep (although you will not be able to
view the lightstep traces unless you have an access token).

Open two terminals and navigate to this directory. Run the following commands in
each terminal:

First window:

``` 
> export FLASK_APP=responder.py   
> flask run 
```

Second window:

``` 
> export FLASK_APP=requester.py   
> flask run --port=0 
```

To test the traces, check what port the requester is running on and load
localhost:port. If you have a lightstep tracer token, you
should be able to view the trace data on the lightstep interface. 
(NOTE: if you wish to use a different OpenTracing tracer, simply replace
`ls_tracer` with the OpenTracing tracer instance of your choice.)

### Trace a request:

Navigate to `/request/simple/<int:numrequests>` where numrequests is the number
of requests you want to send to the page. This will send a request to the server
app, and the trace will include a span on both the client and server sides. This
occurs automatically since both the client and server functions are decorated
with @tracer.trace().

### Log something to a request:

Navigate to `/log`. This will log a message to the server-side span. The client
span is created automatically through the @tracer.trace() decorator, while the
logging occurs within the function by accessing the current span as follows:

```python
span = tracer.get_span()
span.log_event("hello world")
```

### Add spans to the trace manually:

Navigate to `/request/childspan/<int:numrequests>`. This will send a request to
the server app, and the trace will include a span on both the client and server
sides. The server app will additionally create a child span for the server-side
span. This example demonstrates how you can trace non-RPC function calls in your
app, through accessing the current span as follows:

```python
parent_span = tracer.get_span()
child_span = ls_tracer.start_span("inside create_child_span", parent_span)
... do some stuff
child_span.finish()	
```
