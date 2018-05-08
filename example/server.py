import opentracing
import logging
from jaeger_client import Config
from flask_opentracing import FlaskTracer
from opentracing.propagation import Format
from flask import Flask, request
from opentracing.ext import tags
from os import environ

JAEGER_HOST = environ.get('JAEGER_HOST')

if __name__ == '__main__':
        app = Flask(__name__)
        log_level = logging.DEBUG
        logging.getLogger('').handlers = []
        logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)
        config = Config(config={'sampler': {'type': 'const', 'param': 1},
                                'logging': True,
                                'local_agent':
                                {'reporting_host': JAEGER_HOST}},
                        service_name="jaeger_opentracing_example")
        ls_tracer = config.initialize_tracer()
        tracer = FlaskTracer(ls_tracer)

        @app.route('/log')
        @tracer.trace()
        def log():

                span_ctx = ls_tracer.extract(Format.HTTP_HEADERS, request.headers)
                print(request.headers)
                span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}
                print(span_tags)
                child_span = ls_tracer.start_span("python webserver internal span of log method",
                                                  child_of=span_ctx,
                                                  tags=span_tags)
                #do some things here
                child_span.finish()
                return "log"

        app.run(debug=True, host='0.0.0.0', port=5000)
