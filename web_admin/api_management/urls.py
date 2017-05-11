from api_management.views import APIListView

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'api_management'

urlpatterns = [
    url(r'^$', login_required(APIListView.as_view(), login_url='login'), name="api_list"),
]
