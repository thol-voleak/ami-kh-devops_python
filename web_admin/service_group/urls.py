from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.service_group_list import ListView
from .views.add_service_group import ServiceGroupCreate

app_name = 'service_group'

urlpatterns = [
    url(r'^list/$', login_required(ListView.as_view(), login_url='login'), name="service_group_list"),
    url(r'^add/$', login_required(ServiceGroupCreate.as_view(), login_url='login'), name="add_service_group"),
]
