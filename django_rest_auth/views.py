from django.contrib.auth import login as django_login
from django.conf import settings
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import get_token_model
from .app_settings import LoginSerializer


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_scope = 'django_rest_auth'
    user = None
    access_token = None
    token = None

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):
            if getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False):
                # TODO Create a JWT Serializer with an expiration
                pass
            else:
                # TODO Create a JWT Serializer
                pass
        else:
            # TODO Create a Token Serializer
            pass

    def login(self):
        self.user = self.serializer.validated_data['user']
        token_model = get_token_model()

        if getattr(settings, 'REST_USE_JWT', False):
            # TODO create a JWT encode function
            pass
        elif token_model:
            # TODO Create a create_token function
            pass

        if getattr(settings, 'REST_SESSION_LOGIN', False):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_simplejwt.settings import (
                api_settings as jwt_settings
            )
            access_token_expiration = (
                timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
            refresh_token_expiration = (
                timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
            return_expiration_times = getattr(
                settings, 'JWT_AUTH_RETURN_EXPIRATION', False)
            auth_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', False)

            data = {
                'user': self.user,
                'access_token': self.access_token
            }

            if not auth_httponly:
                data['refresh_token'] = self.refresh_token
            else:
                data['refresh_token'] = ""

            if return_expiration_times:
                data['access_token_expiration'] = access_token_expiration
                data['refresh_token_expiration'] = refresh_token_expiration

            serializer = serializer_class(
                instance=data,
                context=self.get_serializer_context()
            )
        elif self.token:
            serializer = serializer_class(
                instance=self.token,
                context=self.get_serializer_context()
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTEXT)

        response = Response(serializer.data, status=status.HTTP_200_OK)

        if getattr(settings, 'REST_USE_JWT', False):
            # TODO Create a function for setting jwt_cookies
            pass
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request_data())
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()
