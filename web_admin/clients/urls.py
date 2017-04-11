from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.create import ClientCreate
from .views.detail import DetailView
from .views.update import ClientUpdate, ClientUpdateForm
from .api import ClientApi
from .views.suspend import suspend
from .views.activate import activate
from .views.scope import ScopeList

app_name = 'clients'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="client-list"),
    url(r'^create/$', login_required(ClientCreate.as_view(), login_url='login'), name="create-client"),
    url(r'^(?P<client_id>[^/]+)/delete/$', login_required(ClientApi.delete_client_by_id, login_url='login'),
        name="delete-client"),
    url(r'^details/(?P<client_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='login'),
        name="client-detail"),
    url(r'^update/(?P<client_id>[0-9A-Za-z]+)/$', login_required(ClientUpdateForm.as_view(), login_url='login'),
        name="client-info"),
    url(r'^(?P<client_id>[0-9A-Za-z]+)/credentials/$', login_required(ClientApi.regenerate, login_url='login'),
        name="regenerate-client-secret"),
    url(r'^update/$', login_required(ClientUpdate.as_view(), login_url='login'), name="update-client"),
    url(r'^suspend/(?P<client_id>[0-9A-Za-z]+)/$', login_required(suspend, login_url='login'),
        name="suspend-client"),
    url(r'^activate/(?P<client_id>[0-9A-Za-z]+)/$', login_required(activate, login_url='login'),
        name="activate-client"),
    url(r'^scopes/(?P<client_id>[0-9A-Za-z]+)/$', login_required(ScopeList.as_view(), login_url='login'),
        name="scope-client"),
]
