from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.urls import exceptions as url_exceptions
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string
from rest_framework import serializers, exceptions

from .models import TokenModel

UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        # print("*******", type(authenticate(self.context['request'], **kwargs)))
        # print("************", authenticate(self.context['request'], **kwargs))
        # print("************", self.context)
        # print("*************", kwargs)

        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
            print("u")
        else:
            msg = _('Must include email and password')
            raise exceptions.ValidationError(msg)
        return user

    def _validate_username(self, username, password):
        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include username and password')
            raise exceptions.ValidationError(msg)
        return user

    def _validate_username_email(self, username, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password"')
            raise exceptions.ValidationError(msg)
        return user

    def get_auth_user_using_allauth(self, username, email, password):
        from allauth.account import app_settings

        print("*******", app_settings)

        # Authentication through email
        # print("*****", app_settings.AUTHENTICATION_METHOD)
        # print("*****", app_settings.AuthenticationMethod.EMAIL)
        if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
            return self._validate_email(email, password)

        # print("******", app_settings.AuthenticationMethod.USERNAME)
        # Authentication through username
        if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
            return self._validate_username(username, password)

        # Authentication either thorough username or email
        return self._validate_username_email(username, email, password)

    def get_auth_user_using_orm(self, username, email, password):
        if email:
            try:
                username = UserModel.objects.get(
                    email__iexact=email).get_username()
                # print("******", username.)
            except UserModel.DoesNotExist:
                pass

        if username:
            return self._validate_username_email(username, '', password)
        return None

    def get_auth_user(self, username, email, password):
        """
        Retrieves the auth user from given POST payload by using 
        either `allauth` scheme or bare django scheme.

        Returns the authenticated user instance if credentials are correct
        else `None` will be returned
        """

        if 'allauth' in settings.INSTALLED_APPS:
            # When `is_active` of a user is set to False, allauth tries to return template
            # which does not exists This is the solution for it

            try:
                self.get_auth_user_using_allauth(username, email, password)
            except url_exceptions.NoReverseMatch:
                msg = _('Unable to login with provided credentials')
                raise exceptions.ValidationError
        return self.get_auth_user_using_orm(username, email, password)

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = _('User account is disabled')
            raise exceptions.ValidationError(msg)

    @staticmethod
    def validate_email_verification_status(user):
        from allauth.account import app_settings
        # print("******", app_settings.EMAIL_VERIFICATION)
        # print("********", app_settings.EmailVerificationMethod.MANDATORY)
        if (
            app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY
            and user.emailaddress_set.filter(email=user.email, verfified=True).exists()
        ):
            raise serializers.ValidationError(_('Email not verified'))

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        user = self.get_auth_user(username, email, password)

        if not user:
            msg = _('Unable to login with provided credentials')
            raise exceptions.ValidationError(msg)

        # Did we get an active user back?
        self.validate_auth_user_status(user)

        # If required, is the email verified
        if 'dj_rest_auth.registration ' in settings.INSTALLED_APPS:
            self.validate_email_verification_status(user)

        attrs['user'] = user

        # print(attrs)

        return attrs


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model with/without password
    """
    @staticmethod
    def validate_username(username):
        if 'allauth.account' not in settings.INSTALLED_APPS:
            return username

        from allauth.account.adapter import get_adapter
        username = get_adapter().clean_username(username)
        return username

    class Meta:
        extra_fields = []
        if hasattr(UserModel, 'USERNAME_FIELD'):
            extra_fields.append(UserModel.USERNAME_FIELD)
        if hasattr(UserModel, 'EMAIL_FIELD'):
            extra_fields.append(UserModel.EMAIL_FIELD)
        if hasattr(UserModel, 'first_name'):
            extra_fields.append('first_name')
        if hasattr(UserModel, 'last_name'):
            extra_fields.append('last_name')
        model = UserModel
        fields = ('pk', *extra_fields)
        # print("***********", fields)
        read_only_fields = ('email',)


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication
    """
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """
        Required to allow using custom USER_DETAILS_SERIALIZER in
        JWTSerializer. Defining it here to avoid circular imports
        """
        rest_auth_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})
        JWTUserDetailsSerializer = import_string(rest_auth_serializers.get(
            'USER_DETAILS_SERIALIZER',
            'django_rest_auth.serializers.UserDetailsSerializer')
        )
        # print("************", obj["user"].__dict__)
        user_data = JWTUserDetailsSerializer(
            obj['user'], context=self.context).data

        # print("********", self.context)
        # print("**********", obj['user'])
        # print("**********", user_data)

        return user_data


class JWTSerializerWithExpiration(JWTSerializer):
    """
    Serializer for JWT authentication with expiration times
    """
    access_token_expiration = serializers.DateTimeField()
    refresh_token_expiration = serializers.DateTimeField()


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """
    class Meta:
        model = TokenModel
        # print("*************", model.objects.all())
        fields = ('key',)
