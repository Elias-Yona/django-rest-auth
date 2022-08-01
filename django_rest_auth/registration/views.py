from rest_framework.generics import CreateAPIView

from .app_settings import RegisterSerializer, register_permission_classes


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = register_permission_classes()
