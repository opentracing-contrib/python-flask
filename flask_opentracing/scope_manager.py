from __future__ import absolute_import

from flask import _request_ctx_stack as stack

from opentracing.scope_managers import ThreadLocalScopeManager
from opentracing import Scope


class FlaskScopeManager(ThreadLocalScopeManager):
    """
    opentracing.ScopeManager implementation for Flask that stores
    the opentracing.Scope in a Flask RequestContext, made accessible
    via flask._request_ctx_stack.
    """
    @property
    def _context(self):
        # Default to ThreadLocalScopeManager._tls_scope for usage outside
        # app/request context (unit tests)
        if stack.top is None:
            return self._tls_scope
        return stack.top

    @property
    def _active_attr(self):
        """
        Make an instance-specific attribute with which to pin active
        opentracing.Scope.  Necessary in cases of multiple tracers,
        to prevent scope creep.
        """
        return '__ot_{0}'.format(id(self))

    def activate(self, span, finish_on_close):
        """
        Make a opentracing.Span instance active. Returns an opentracing.Scope
        instance to control the end of the active period for the
        opentracing.Span. It is a programming error to neglect to call
        Scope.close() on the returned instance.

        @param span the opentracing.Span that should become active.
        @param finish_on_close whether span should automatically be finished
         when Scope.close() is called.

        """
        scope = _FlaskScope(self, span, finish_on_close)
        setattr(self._context, self._active_attr, scope)
        return scope

    @property
    def active(self):
        """
        Returns the currently active opentracing.Scope which can be used to
        access the currently active Scope.span or None if not available.
        """
        return getattr(self._context, self._active_attr, None)


class _FlaskScope(Scope):

    def __init__(self, manager, span, finish_on_close):
        super(_FlaskScope, self).__init__(manager, span)
        self._finish_on_close = finish_on_close
        self._to_restore = manager.active

    def close(self):
        if self.manager.active is not self:
            return

        if self._finish_on_close:
            self.span.finish()

        setattr(self.manager._context, self.manager._active_attr,
                self._to_restore)
