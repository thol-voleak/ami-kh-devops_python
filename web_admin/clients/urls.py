from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.create import ClientCreate

app_name = 'clients'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="client-list"),
    url(r'^create/$', login_required(ClientCreate.as_view(), login_url='login'), name="create-client"),
]