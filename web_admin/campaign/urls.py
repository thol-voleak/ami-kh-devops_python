from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import CamPaignList



app_name = 'campaign'

urlpatterns = [
    url(r'^$', login_required(CamPaignList.as_view(), login_url='authentications:login'), name="campaign"),
]

