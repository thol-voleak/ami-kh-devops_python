from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.service_group_list import ListView

from .views.add_service_group import ServiceGroupCreate
from .views.update import ServiceGroupUpdateForm
from .views.detail import ServiceGroupDetailForm


app_name = 'service_group'

urlpatterns = [
    url(r'^list/$', login_required(ListView.as_view(), login_url='login'), name="service_group_list"),
    url(r'^add/$', login_required(ServiceGroupCreate.as_view(), login_url='login'), name="add_service_group"),
    url(r'^(?P<ServiceGroupId>[0-9A-Za-z]+)/update/$', login_required(ServiceGroupUpdateForm.as_view(), login_url='login'),
        name="service_group_update"),
    url(r'^(?P<ServiceGroupId>[0-9A-Za-z]+)/details/$', login_required(ServiceGroupDetailForm.as_view(), login_url='login'),
        name="service_group_detail"),
]
