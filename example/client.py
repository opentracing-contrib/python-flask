import sys
if sys.version_info[:2] >= (3, 10):
    # compat for Python written pre-3.10
    import collections
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping

import requests
import time
from opentracing_instrumentation.client_hooks import install_all_patches
from jaeger_client import Config

from os import getenv

JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')
WEBSERVER_HOST = getenv('WEBSERVER_HOST', 'localhost')

# Create configuration object with enabled logging and sampling of all requests.
config = Config(config={'sampler': {'type': 'const', 'param': 1},
                        'logging': True,
                        'local_agent': {'reporting_host': JAEGER_HOST}},
                service_name="jaeger_opentracing_example")
tracer = config.initialize_tracer()

# Automatically trace all requests made with 'requests' library.
install_all_patches()

url = "http://{}:5000/log".format(WEBSERVER_HOST)
# Make the actual request to webserver.
requests.get(url)

# allow tracer to flush the spans - https://github.com/jaegertracing/jaeger-client-python/issues/50
time.sleep(2)
tracer.close()
