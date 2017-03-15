from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.create import ClientCreate
from .views.detail import DetailView
from .views.update import ClientUpdate, ClientUpdateForm
from .api import ClientApi

app_name = 'clients'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="client-list"),
    url(r'^create/$', login_required(ClientCreate.as_view(), login_url='login'), name="create-client"),
    url(r'^details/(?P<client_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='login'),
        name="client-detail"),
    url(r'^update/(?P<client_id>[0-9A-Za-z]+)/$', login_required(ClientUpdateForm.as_view(), login_url='login'),
        name="client-info"),
    url(r'^(?P<client_id>[0-9A-Za-z]+)/credentials/$', login_required(ClientApi.regenerate, login_url='login'), name="regenerate-client-secret"),
    url(r'^update/$', login_required(ClientUpdate.as_view(), login_url='login'), name="update-client"),
]
