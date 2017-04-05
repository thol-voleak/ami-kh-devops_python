from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views.create import CreateView
from .views.services_list import ListView

app_name = "services"


urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="services_list"),
    url(r'^add/$', login_required(CreateView.as_view(), login_url='login'), name="service_create"),
]
