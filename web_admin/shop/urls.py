from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from shop.views.ajax import Agent_Detail
from .views.create import CreateView
from .views.delete import DeleteView
from .views.detail import DetailView
from .views.edit import EditView
from .views.list import ListView
from .views.device_update import DeviceUpdateView
from .views.add_device import AddDeviceView
from .views.device_management_ajax import grant_channel_access, revoke_channel_access, enable_device, disable_device, unbind_device

app_name = 'shop'

urlpatterns = [
url(r'^ajax/agent-detail/(?P<id>[0-9A-Za-z]+)/$', login_required(Agent_Detail.as_view(), login_url='authentications:login'), name="ajax_agent_detail"),
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="shop_list"),
    url(r'^create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="shop_create"),
    url(r'^(?P<id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="shop_edit"),
    url(r'^(?P<id>[0-9A-Za-z]+)/detail/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="shop_detail"),
    url(r'^(?P<id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'), name="shop_delete"),
    url(r'^(?P<id>[0-9A-Za-z]+)/devices/(?P<device_id>[0-9A-Za-z]+)/edit', login_required(DeviceUpdateView.as_view(), login_url='authentications:login'), name="device_update"),
    url(r'^(?P<shop_id>[0-9A-Za-z]+)/channels/(?P<channel_id>[0-9A-Za-z]+)/grant$', login_required(grant_channel_access, login_url='authentications:login'), name="grant_channel_access"),
    url(r'^(?P<shop_id>[0-9A-Za-z]+)/channels/(?P<channel_id>[0-9A-Za-z]+)/revoke$', login_required(revoke_channel_access, login_url='authentications:login'), name="revoke_channel_access"),
    url(r'^devices/(?P<device_id>[0-9A-Za-z]+)/enable$', login_required(enable_device, login_url='authentications:login'), name="enable_device"),
    url(r'^devices/(?P<device_id>[0-9A-Za-z]+)/disable$', login_required(disable_device, login_url='authentications:login'), name="disable_device"),
    url(r'^devices/(?P<device_id>[0-9A-Za-z]+)/unbind$', login_required(unbind_device, login_url='authentications:login'), name="unbind_device"),
    url(r'^(?P<shop_id>[0-9A-Za-z]+)/devices$', login_required(AddDeviceView.as_view(), login_url='authentications:login'), name="add_device"),
]
