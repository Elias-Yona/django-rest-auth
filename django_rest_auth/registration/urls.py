from django.urls import path, re_path
from django.views.generic import TemplateView

from .views import RegisterView


urlpatterns = [
    path('', RegisterView.as_view(), name='rest_register'),

    # This url is used by django-allauth and empty TemplateView is
    # defined just to allow reverse() call inside app, for example when email
    # with verification link is being sent, then it's required to render email
    # content.
    re_path(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$', TemplateView.as_view(),
        name='account_confirm_email',
    ),
    path('account-email-verification-sent/', TemplateView.as_view(),
         name='account_email_verification_sent')

]
