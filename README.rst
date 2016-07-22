#################
Flask-OpenTracing
#################

This package enables distributed tracing in Flask applications via `The OpenTracing Project`_. Once a production system contends with real concurrency or splits into many services, crucial (and formerly easy) tasks become difficult: user-facing latency optimization, root-cause analysis of backend errors, communication about distinct pieces of a now-distributed system, etc. Distributed tracing follows a request on its journey from inception to completion from mobile/browser all the way to the microservices. 

As core services and libraries adopt OpenTracing, the application builder is no longer burdened with the task of adding basic tracing instrumentation to their own code. In this way, developers can build their applications with the tools they prefer and benefit from built-in tracing instrumentation. OpenTracing implementations exist for major distributed tracing systems and can be bound or swapped with a one-line configuration change.

If you want to learn more about the underlying python API, visit the python `source code`_.

.. _The OpenTracing Project: http://opentracing.io/
.. _source code: https://github.com/opentracing/opentracing-python

Installation
============

Run the following command:

.. code-block:: 

    $ pip install Flask-Opentracing

Usage
=====

This Flask extension allows for tracing of Flask apps using the OpenTracing API. All
that it requires is for a FlaskTracing tracer to be initialized using an
instance of an OpenTracing tracer. You can either trace all requests to your site, or use function decorators to trace certain individual requests.

**Note:** `optional_args` in both cases are any number of attributes (as strings) of `flask.Request` that you wish to set as tags on the created span

Trace All Requests
------------------

.. code-block:: python

    import opentracing
    from flask_opentracing import FlaskTracer

    app = Flask(__name__)

    opentracing_tracer = ## some OpenTracing tracer implementation
    tracer = FlaskTracer(opentracing_tracer, True, app, [optional_args])

Trace Individual Requests
-------------------------

.. code-block:: python

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

Accessing Spans Manually
------------------------

In order to access the span for a request, we've provided an method `FlaskTracer.get_span(request)` that returns the span for the request, if it is exists and is not finished. This can be used to log important events to the span, set tags, or create child spans to trace non-RPC events. If no request is passed in, the current request will be used.

Tracing an RPC
--------------

If you want to make an RPC and continue an existing trace, you can inject the current span into the RPC. For example, if making an http request, the following code will continue your trace across the wire:

.. code-block:: python

    @tracer.trace()
    def some_view_func(request):
        new_request = some_http_request
        current_span = tracer.get_span(request)
        text_carrier = {}
        opentracing_tracer.inject(span, opentracing.Format.TEXT_MAP, text_carrier)
        for k, v in text_carrier.iteritems():
            request.add_header(k,v)
        ... # make request

Examples
========

See `examples`_ to view and run an example of two Flask applications
with integrated OpenTracing tracers.

.. _examples: https://github.com/opentracing-contrib/python-flask/tree/master/example

Further Information
===================

If you’re interested in learning more about the OpenTracing standard, please visit `opentracing.io`_ or `join the mailing list`_. If you would like to implement OpenTracing in your project and need help, feel free to send us a note at `community@opentracing.io`_.

.. _opentracing.io: http://opentracing.io/
.. _join the mailing list: http://opentracing.us13.list-manage.com/subscribe?u=180afe03860541dae59e84153&id=19117aa6cd
.. _community@opentracing.io: community@opentracing.io

