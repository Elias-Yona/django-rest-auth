from django.urls import path
from django.conf import settings
from .views import (LoginView, LogoutView, UserDetailsView,
                    PasswordChangeView, PasswordResetView)

urlpatterns = [
    path("login/", LoginView.as_view(), name="rest_login"),
    path('password/reset/', PasswordResetView.as_view(),
         name='rest_password_reset'),
    # URLs that require a user to be logged in with a valid session / token.
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('user/', UserDetailsView.as_view(), name='rest_user_details'),
    path('password/change/', PasswordChangeView.as_view(),
         name='rest_password_change'),
]

if getattr(settings, 'REST_USE_JWT', False):
    from rest_framework_simplejwt.views import TokenVerifyView

    from django_rest_auth.jwt_auth import get_refresh_view

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path('token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
    ]
