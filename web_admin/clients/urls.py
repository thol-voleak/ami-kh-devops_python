from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views import ListView, CreateView
from . import views

app_name = 'clients'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="client-list"),
    url(r'^create/$', login_required(CreateView.as_view(), login_url='login'), name="create-client"),
]