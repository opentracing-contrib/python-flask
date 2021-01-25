#################
Flask-OpenTracing
#################

This package enables distributed tracing in Flask applications via `The OpenTracing Project`_. Once a production system contends with real concurrency or splits into many services, crucial (and formerly easy) tasks become difficult: user-facing latency optimization, root-cause analysis of backend errors, communication about distinct pieces of a now-distributed system, etc. Distributed tracing follows a request on its journey from inception to completion from mobile/browser all the way to the microservices. 

As core services and libraries adopt OpenTracing, the application builder is no longer burdened with the task of adding basic tracing instrumentation to their own code. In this way, developers can build their applications with the tools they prefer and benefit from built-in tracing instrumentation. OpenTracing implementations exist for major distributed tracing systems and can be bound or swapped with a one-line configuration change.

If you want to learn more about the underlying python API, visit the python `source code`_.

If you are migrating from the 0.x series, you may want to read the list of `breaking changes`_.

.. _The OpenTracing Project: http://opentracing.io/
.. _source code: https://github.com/opentracing/opentracing-python
.. _breaking changes: #breaking-changes-from-0-x

Installation
============

Run the following command:

.. code-block:: 

    $ pip install signalfx-instrumentation-flask

Usage
=====

This Flask extension allows for tracing of Flask apps using the OpenTracing API. All
that it requires is for a ``FlaskTracing`` tracer to be initialized using an
instance of an OpenTracing tracer. You can either trace all requests to your site, or use function decorators to trace certain individual requests.

**Note:** `optional_args` in both cases are any number of attributes (as strings) of `flask.Request` that you wish to set as tags on the created span

Initialize
----------

`FlaskTracing` wraps the tracer instance that's supported by opentracing. To create a `FlaskTracing` object, you can either pass in a tracer object directly or a callable that returns the tracer object. For example:

.. code-block:: python

    import opentracing
    from flask_opentracing import FlaskTracing

    opentracing_tracer = ## some OpenTracing tracer implementation
    tracing = FlaskTracing(opentracing_tracer, ...)

or

.. code-block:: python

    import opentracing
    from flask_opentracing import FlaskTracing

    def initialize_tracer():
        ...
        return opentracing_tracer

    tracing = FlaskTracing(initialize_tracer, ...)


Trace All Requests
------------------

.. code-block:: python

    import opentracing
    from flask_opentracing import FlaskTracing

    app = Flask(__name__)

    opentracing_tracer = ## some OpenTracing tracer implementation
    tracing = FlaskTracing(opentracing_tracer, True, app, [optional_args])

Trace Individual Requests
-------------------------

.. code-block:: python

    import opentracing
    from flask_opentracing import FlaskTracing

    app = Flask(__name__)

    opentracing_tracer = ## some OpenTracing tracer implementation  
    tracing = FlaskTracing(opentracing_tracer)

    @app.route('/some_url')
    @tracing.trace(optional_args)
    def some_view_func():
    	...     
    	return some_view 

Accessing Spans Manually
------------------------

In order to access the span for a request, we've provided an method `FlaskTracing.get_span(request)` that returns the span for the request, if it is exists and is not finished. This can be used to log important events to the span, set tags, or create child spans to trace non-RPC events. If no request is passed in, the current request will be used.

Tracing an RPC
--------------

If you want to make an RPC and continue an existing trace, you can inject the current span into the RPC. For example, if making an http request, the following code will continue your trace across the wire:

.. code-block:: python

    @tracing.trace()
    def some_view_func(request):
        new_request = some_http_request
        current_span = tracing.get_span(request)
        text_carrier = {}
        opentracing_tracer.inject(span, opentracing.Format.TEXT_MAP, text_carrier)
        for k, v in text_carrier.iteritems():
            new_request.add_header(k,v)
        ... # make request

FlaskScopeManager
-----------------

By default, Flask-OpenTracing will attempt to track spans initiated by view functions in the request context.  However, to fully ensure parent-child span relationships throughout your Flask application in any deployment configuration, a FlaskScopeManager is provided.

.. code-block:: python

    from my_opentracing_tracer import OpenTracingTracer
    from flask_opentracing import FlaskTracer, FlaskScopeManager

    app = Flask(__name__)

    opentracing_tracer = OpenTracingTracer(FlaskScopeManager())
    # trace all requests
    tracing = FlaskTracing(opentracing_tracer, True, app, [optional_args])

    @app.route('/some_url')
    def some_view_func():
        helper_function()
        ...
        return some_view


    def helper_function():
        # spans created in your application will be children of parent spans
        # automatically created for your traced view function.
        with opentracing_tracer.start_active_span('MyChildSpan') as scope
            scope.span.set_tag('HelpfulKey', 'HelpfulValue')

Examples
========

See `examples`_ to view and run an example of two Flask applications
with integrated OpenTracing tracers.

.. _examples: https://github.com/opentracing-contrib/python-flask/tree/master/example

`This tutorial <http://blog.scoutapp.com/articles/2018/01/15/tutorial-tracing-python-flask-requests-with-opentracing>`_ has a step-by-step guide for using `Flask-Opentracing` with `Jaeger <https://github.com/jaegertracing/jaeger>`_.

Breaking changes from 0.x
=========================

Starting with the 1.0 version, a few changes have taken place from previous versions:

* ``FlaskTracer`` has been renamed to ``FlaskTracing``, although ``FlaskTracing``
  can be used still as a deprecated name.
* When passing an ``Application`` object at ``FlaskTracing`` creation time,
  ``trace_all_requests`` defaults to ``True``.
* When no ``opentracing.Tracer`` is provided, ``FlaskTracing`` will rely on the
  global tracer.

Further Information
===================

If you're interested in learning more about the OpenTracing standard, please visit `opentracing.io`_ or `join the mailing list`_. If you would like to implement OpenTracing in your project and need help, feel free to send us a note at `community@opentracing.io`_.

.. _opentracing.io: http://opentracing.io/
.. _join the mailing list: http://opentracing.us13.list-manage.com/subscribe?u=180afe03860541dae59e84153&id=19117aa6cd
.. _community@opentracing.io: community@opentracing.io

