from rest_framework.authentication import SessionAuthentication
from rest_framework.throttling import AnonRateThrottle
class StrictSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        # SessionAuthentication alone does not enforce CSRF on anonymous login.
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            self.enforce_csrf(request)
        return super().authenticate(request)
class AuthThrottle(AnonRateThrottle):
    scope = 'auth'
    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}
