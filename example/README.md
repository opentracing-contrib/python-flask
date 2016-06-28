This example has two flask sites and shows they can trace requests both within
and between the two sites using the flask-opentracing extension, a concrete
variant of an OpenTracing tracer, and the OpenTracing API. To run, make sure
that you run pip install for flask, opentracing, and lightstep (although you
will not be able to view the lightstep traces unless you have an access token).

Open two terminals and navigate to this directory. Run the following commands in
each terminal:

First window:

> export FLASK_APP=responder.py 
> flask run

Second window:

> export FLASK_APP=requester.py 
> flask run --port=0

To test the traces, check what port the requester is running on and load
localhost:port. Then navigate to /request/<script>/<int:numrequests> where
script can either be "simple" or "childspan" and numrequests is the number of
requests you want to send to the page. If you have a lightstep tracer token, you
should be able to view the trace data on the lightstep interface. Otherwise, the
commandline will print the trace information.

(NOTE: if you wish to use a different opentracing tracer, simply replace
ls_tracer with the OpenTracing tracer instance of your choice.)
