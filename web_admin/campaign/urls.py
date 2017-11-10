from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import CampaignList
from .views.active import active
from .views.inactive import inactive
from .views.create import CreateCampaignView
from .views.detail import CampaignDetail
from .views.add_mechanic import AddMechanic
from .api import CampaignApi


app_name = 'campaign'

urlpatterns = [
    url(r'^$', login_required(CampaignList.as_view(), login_url='authentications:login'), name="campaign"),
    url(r'^inactive/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(inactive, login_url='authentications:login'),
        name="inactive-campaign"),
    url(r'^active/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(active, login_url='authentications:login'),
        name="activate-campaign"),
    url(r'^detail/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(CampaignDetail.as_view(), login_url='authentications:login'),
        name="campaign_detail"),
    url(r'^campaign/create$', login_required(CreateCampaignView.as_view(), login_url='authentications:login'),
        name="create_campaign"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/add_mechanic$', login_required(AddMechanic.as_view(), login_url='authentications:login'),
        name="add_mechanic"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/delete/(?P<mechanic_id>[0-9A-Za-z]+)/$', login_required(CampaignApi.delete_mechanic_by_id, login_url='authentications:login'),
        name="delete_mechanic"),
]

