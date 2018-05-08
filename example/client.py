import requests
import time
from opentracing_instrumentation.client_hooks import install_all_patches
from opentracing_instrumentation.request_context import get_current_span, span_in_context
from jaeger_client import Config
from opentracing.ext import tags
from opentracing.propagation import Format

from os import environ

JAEGER_HOST = environ.get('JAEGER_HOST')

WEBSERVER_HOST = environ.get('WEBSERVER_HOST')

config = Config(config={'sampler': {'type': 'const', 'param': 1},
                        'logging': True,
                        'local_agent': {'reporting_host': JAEGER_HOST}},
                service_name="jaeger_opentracing_example")
tracer = config.initialize_tracer()

install_all_patches()

url = "http://{}:5000/log".format(WEBSERVER_HOST)
with tracer.start_span('say-hello') as span:
    span.set_tag(tags.HTTP_METHOD, 'GET')
    span.set_tag(tags.HTTP_URL, url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_CLIENT)
    headers = {}
    tracer.inject(span, Format.HTTP_HEADERS, headers)

    r = requests.get(url, headers=headers)
    print(r.text)

    time.sleep(2)
    tracer.close()
