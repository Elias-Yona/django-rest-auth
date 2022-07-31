from django.contrib.auth import login as django_login
from django.conf import settings
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import get_token_model
from .app_settings import (
    LoginSerializer, JWTSerializerWithExpiration, JWTSerializer, TokenSerializer, create_token
)
from .utils import jwt_encode


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
                response_serializer = JWTSerializerWithExpiration
            else:
                response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']
        # print("*****", self.serializer)
        # print("*****", self.user)
        # print("*****", type(self.user))
        token_model = get_token_model()
        # print("*******", token_model)

        if getattr(settings, 'REST_USE_JWT', False):
            self.access_token, self.refresh_token = jwt_encode(self.user)
            # print("*********", self.access_token)
            # print("*********", self.refresh_token)
        elif token_model:
            self.token = create_token(token_model, self.user)
        if getattr(settings, 'REST_SESSION_LOGIN', False):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()
        # print("********", serializer_class)

        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_simplejwt.settings import (
                api_settings as jwt_settings
            )
            access_token_expiration = (
                timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
            # print("*****", access_token_expiration)
            refresh_token_expiration = (
                timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
            # print("*****", access_token_expiration)
            return_expiration_times = getattr(
                settings, 'JWT_AUTH_RETURN_EXPIRATION', False)
            auth_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', False)

            data = {
                'user': self.user,
                'access_token': self.access_token
            }

            # print("*********", data)

            if not auth_httponly:
                data['refresh_token'] = self.refresh_token
                # print("********", self.refresh_token)
            else:
                data['refresh_token'] = ""

            if return_expiration_times:
                data['access_token_expiration'] = access_token_expiration
                data['refresh_token_expiration'] = refresh_token_expiration

            # print("*******", data)
            serializer = serializer_class(
                instance=data,
                context=self.get_serializer_context()
            )
            # print("******", serializer)
        elif self.token:
            serializer = serializer_class(
                instance=self.token,
                context=self.get_serializer_context()
            )
            # print("***********", serializer.instance)
            # print("***********", serializer.context)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

        response = Response(serializer.data, status=status.HTTP_200_OK)

        # print("********", response.__dict__)

        if getattr(settings, 'REST_USE_JWT', False):
            from .jwt_auth import set_jwt_cookies
            set_jwt_cookies(response, self.access_token, self.refresh_token)

        # print("********", response.__dict__['cookies'])
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        # print("********************", request.data)
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        # print("********************", self.serializer)

        self.login()
        return self.get_response()
