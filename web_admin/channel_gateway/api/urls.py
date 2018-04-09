from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from channel_gateway.api.views.create import CreateView
from channel_gateway.api.views.delete import DeleteView
from channel_gateway.api.views.detail import DetailView
from channel_gateway.api.views.edit import EditView
from channel_gateway.api.views.list import ListView

app_name = 'channel_gateway_api'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="list"),
    url(r'^create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="create"),
    url(r'^(?P<shop_type_id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="edit"),
    url(r'^(?P<id>[0-9A-Za-z]+)/detail/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="detail"),
    url(r'^(?P<id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'), name="delete"),
]
