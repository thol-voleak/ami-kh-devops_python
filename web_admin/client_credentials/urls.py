from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views import ListView

app_name = 'client_credentials'

urlpatterns = [
    url(r'$', login_required(ListView.as_view(), login_url='login'), name="client-list"),
]