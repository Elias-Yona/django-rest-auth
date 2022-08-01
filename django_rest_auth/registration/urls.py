from django.urls import path, re_path

from .views import RegisterView


urlpatterns = [
    path('', RegisterView.as_view(), name='rest_register'),
]
