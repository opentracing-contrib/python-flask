import logging
from jaeger_client import Config
from flask_opentracing import FlaskTracer
from flask import Flask, request
from os import getenv
JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')

if __name__ == '__main__':
        app = Flask(__name__)
        log_level = logging.DEBUG
        logging.getLogger('').handlers = []
        logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
        # Create configuration object with enabled logging and sampling of all requests.
        config = Config(config={'sampler': {'type': 'const', 'param': 1},
                                'logging': True,
                                'local_agent':
                                # Also, provide a hostname of Jaeger instance to send traces to.
                                {'reporting_host': JAEGER_HOST}},
                        # Service name can be arbitrary string describing this particular web service.
                        service_name="jaeger_opentracing_example")
        jaeger_tracer = config.initialize_tracer()
        tracer = FlaskTracer(jaeger_tracer)

        @app.route('/log')
        # Indicate that /log endpoint should be traced
        @tracer.trace()
        def log():
                # Extract the span information for request object.
                request_span = tracer.get_span(request)
                # Start internal span to trace some kind of business logic for /log.
                current_span = jaeger_tracer.start_span("python webserver internal span of log method",
                                                        child_of=request_span)
                # Perform some computations to be traced.

                a = 1
                b = 2
                c = a + b

                # Finish the current span.
                current_span.finish()
                return "log"

        app.run(debug=True, host='0.0.0.0', port=5000)
