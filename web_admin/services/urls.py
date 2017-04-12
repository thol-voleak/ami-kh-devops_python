from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views.create import CreateView
from .views.services_list import ListView
from .views.detail import ServiceDetailForm
from .views.update import UpdateView


app_name = "services"

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="services_list"),
    url(r'^details/(?P<ServiceId>[0-9A-Za-z]+)/$', login_required(ServiceDetailForm.as_view(), login_url='login'),
        name="service_detail"),
    url(r'^add/$', login_required(CreateView.as_view(), login_url='login'), name="service_create"),
    url(r'^update/(?P<service_id>[0-9A-Za-z]+)/$', login_required(UpdateView.as_view(), login_url='login'),
        name="update_service"),
]
