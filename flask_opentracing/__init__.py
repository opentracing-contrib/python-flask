import warnings

from .tracing import FlaskTracing  # noqa
from .tracing import FlaskTracing as FlaskTracer  # noqa, deprecated

warnings.warn(
     'This package is no longer supported.'
     ' Migrate to using opentelemetry-api.',
     DeprecationWarning,
     stacklevel=2
)
