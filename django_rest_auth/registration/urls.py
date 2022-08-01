from django.urls import path, re_path

from .views import RegisterView, AccountConfirmEmailView


urlpatterns = [
    path('', RegisterView.as_view(), name='rest_register'),

    # This url is used by django-allauth and empty TemplateView is
    # defined just to allow reverse() call inside app, for example when email
    # with verification link is being sent, then it's required to render email
    # content.
    re_path(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$', AccountConfirmEmailView.as_view(),
        name='account_confirm_email',
    ),
]
