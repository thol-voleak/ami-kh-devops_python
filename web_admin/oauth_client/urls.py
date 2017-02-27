from django.conf.urls import url
from .views import ListView

app_name = 'oauth_client'

urlpatterns = [
    url(r'$', ListView.as_view(), name="auth-index"),
]
