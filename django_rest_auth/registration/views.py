from django.utils.translation import gettext_lazy as _
from django.conf import settings
from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response

from django_rest_auth.models import TokenModel
from django_rest_auth.app_settings import (
    JWTSerializer, TokenSerializer,
)
from django_rest_auth.utils import jwt_encode
from django_rest_auth.app_settings import create_token

from .app_settings import RegisterSerializer, register_permission_classes


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = register_permission_classes()
    token_model = TokenModel
    throttle_scope = 'django_rest_auth'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_response_data(self, user):
        # if allauth.account.app_settings.EMAIL_VERIFICATION is the same as
        # allauth.account.app_settings.EMAIL_VERIFICATION.EmailVerificationMethod.MANDATORY
        # then return a dictionary with the value {'detail': _('Verification e-mail sent.')}
        if allauth_settings.EMAIL_VERIFICATION == \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            return {'detail': _('Verification e-mail sent.')}

        # return True if REST_USE_JWT attribute is in settings else False
        if getattr(settings, 'REST_USE_JWT', False):
            # If true initialize data with a dictionary with the following items
            # user -> user
            # access_token -> value of the access token
            # refresh_token -> value of refresh_token
            data = {
                'user': user,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
            }
            return JWTSerializer(data, context=self.get_serializer_context()).data
        elif getattr(settings, 'REST_SESSION_LOGIN', False):
            return None
        else:
            return TokenSerializer(user.auth_token, context=self.get_serializer_context()).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(
                status=status.HTTP_204_NO_CONTENT, headers=headers)
        return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if allauth_settings.EMAIL_VERIFICATION != \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            if getattr(settings, 'REST_USE_JWT', False):
                self.access_token, self.refresh_token = jwt_encode(user)
            elif not getattr(settings, 'REST_SESSION_LOGIN', False):
                # Session authentication isn't active either, so this has to be
                #  token authentication
                create_token(self.token_model, user, serializer)
        complete_signup(
            self.request._request, user,
            allauth_settings.EMAIL_VERIFICATION,
            None,
        )
        return user
