from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import CamPaignList
from .views.active import active
from .views.inactive import inactive


app_name = 'campaign'

urlpatterns = [
    url(r'^$', login_required(CamPaignList.as_view(), login_url='authentications:login'), name="campaign"),
    url(r'^inactive/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(inactive, login_url='authentications:login'),
        name="inactive-campaign"),
    url(r'^active/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(active, login_url='authentications:login'),
        name="activate-campaign"),
]

