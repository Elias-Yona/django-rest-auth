from importlib import import_module
from django.conf import settings


def import_callable(path_or_callable):
    if hasattr(path_or_callable, '__call__'):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, str)
        package, attr = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attr)


def jwt_encode(user):
    from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
    rest_auth_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})

    JWTTokenClaimsSerializer = rest_auth_serializers.get(
        'JWT_TOKEN_CLAIMS_SERIALIZER', TokenObtainPairSerializer)
    TOPS = import_callable(JWTTokenClaimsSerializer)
    refresh = TOPS.get_token(user)
    # print("******************", user.__dict__)
    # print("******************", refresh)
    # print("******************", refresh.access_token)
    # print("******************", refresh.__dict__['_token_backend'].__dict__)
    return refresh.access_token, refresh


def default_create_token(token_model, user, serializer):
    # print("*************", user)
    # print("*****************", serializer)
    token, _ = token_model.objects.get_or_create(user=user)
    # print("*****************", _)
    return token
