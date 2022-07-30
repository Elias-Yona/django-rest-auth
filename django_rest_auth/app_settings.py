from django.conf import settings
from .utils import import_callable

# TODO create a DefaultLogin Serializer

serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})
LoginSerializer = import_callable(serializers.get(
    'LOGIN_SERIALIZER', DefaultLoginSerializer))
