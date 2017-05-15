from api_management.views import APIListView, AddAPIView

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'api_management'

urlpatterns = [
    url(r'^list/$', login_required(APIListView.as_view(), login_url='login'), name="api_list"),
    url(r'^add/$', login_required(AddAPIView.as_view(), login_url='login'), name="api_add"),
]
