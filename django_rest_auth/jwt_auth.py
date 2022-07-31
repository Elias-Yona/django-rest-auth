from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions


class JWTCookieAuthentication(JWTAuthentication):
    """
    An authentication plugin that hopefully authenticates requests through a JSON Web Token
    provided in a request cookie (and through the header as normal with a preference to the
    header).
    """

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        """
        def dummy_get_response(request):  # pragma: no cover
            return None

        check = CSRFCheck(dummy_get_response)
        # populates request.META['CSRF_COOKIE'] which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit message
            raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')

        def authenticate(self, request):
            cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
            header = self.get_header(request)
            if header is None:
                if cookie_name:
                    raw_token = request.COOKIES.get(cookie_name)
                    if getattr(settings, 'JWT_AUTH_COOKIE_ENFORCE_CSRF_ON_UNAUTHENTICATED', False):
                        self.enforce_csrf(request)
                    elif raw_token is not None and getattr(settings, 'JWT_AUTH_COOKIE_USE_CSRF', False):
                        self.enforce_csrf(request)
                else:
                    return None
            else:
                raw_token = self.get_raw_token(header)

            if raw_token is None:
                return None

            # print("**********", validated_token)
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
