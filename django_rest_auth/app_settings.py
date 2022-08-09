from django.conf import settings
from django_rest_auth.serializers import (
    LoginSerializer as DefaultLoginSerializer
)
from django_rest_auth.serializers import (
    JWTSerializerWithExpiration as DefaultJWTSerializerWithExpiration
)
from django_rest_auth.serializers import (
    JWTSerializer as DefaultJWTSerializer
)
from django_rest_auth.serializers import (
    TokenSerializer as DefaultTokenSerializer,
)
from django_rest_auth.serializers import (
    UserDetailsSerializer as DefaultUserDetailsSerializer,
)
from django_rest_auth.serializers import (
    PasswordChangeSerializer as DefaultPasswordChangeSerializer
)
from django_rest_auth.serializers import (
    PasswordResetSerializer as DefaultPasswordResetSerializer
)
from django_rest_auth.serializers import (
    PasswordResetConfirmSerializer as DefaultPasswordResetConfirmSerializer,)


from .utils import import_callable, default_create_token

serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})

LoginSerializer = import_callable(serializers.get(
    'LOGIN_SERIALIZER', DefaultLoginSerializer))

JWTSerializerWithExpiration = import_callable(serializers.get(
    'JWT_SERIALIZER_WITH_EXPIRATION', DefaultJWTSerializerWithExpiration))

JWTSerializer = import_callable(serializers.get(
    'JWT_SERIALIZER', DefaultJWTSerializer
))

TokenSerializer = import_callable(serializers.get(
    'TOKEN_SERIALIZER', DefaultTokenSerializer))

create_token = import_callable(
    getattr(settings, 'REST_AUTH_TOKEN_CREATOR', default_create_token))


UserDetailsSerializer = import_callable(serializers.get(
    'USER_DETAILS_SERIALIZER', DefaultUserDetailsSerializer))

PasswordChangeSerializer = import_callable(
    serializers.get('PASSWORD_CHANGE_SERIALIZER',
                    DefaultPasswordChangeSerializer)
)

PasswordResetSerializer = import_callable(serializers.get(
    'PASSWORD_RESET_SERIALIZER', DefaultPasswordResetSerializer))

PasswordResetConfirmSerializer = import_callable(
    serializers.get(
        'PASSWORD_RESET_CONFIRM_SERIALIZER', DefaultPasswordResetConfirmSerializer,
    ),
)
