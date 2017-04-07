from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views.services_list import ListView
from .views.detail import ServiceDetailForm

app_name = 'services'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="services_list"),
    url(r'^(?P<ServiceId>[0-9A-Za-z]+)/details/$', login_required(ServiceDetailForm.as_view(), login_url='login'),
        name="service_detail"),
]
