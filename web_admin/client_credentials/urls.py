from django.conf.urls import url
from .views import ListView

app_name = 'client_credentials'

urlpatterns = [
    url(r'$', ListView.as_view(), name="client-list"),
]