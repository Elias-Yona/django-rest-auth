from django.conf import settings
from django_rest_auth.serializers import (
    LoginSerializer as DefaultLoginSerializer
)
from django_rest_auth.serializers import (
    JWTSerializerWithExpiration as DefaultJWTSerializerWithExpiration
)

from .utils import import_callable

serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})

LoginSerializer = import_callable(serializers.get(
    'LOGIN_SERIALIZER', DefaultLoginSerializer))

JWTSerializerWithExpiration = import_callable(serializers.get(
    'JWT_SERIALIZER_WITH_EXPIRATION', DefaultJWTSerializerWithExpiration))
