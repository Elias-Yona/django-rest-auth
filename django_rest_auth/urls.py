from django.urls import path
from django.conf import settings
from .views import LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="rest_login")
]

if getattr(settings, 'REST_USE_JWT', False):
    from rest_framework_simplejwt.views import TokenVerifyView

    # TODO Create a refresh_view

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        # TODO refresh_view will be here
    ]
