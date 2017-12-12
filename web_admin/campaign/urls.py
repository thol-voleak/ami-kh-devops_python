from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import CampaignList
from .views.active import ActiveCampaign
from .views.inactive import inactive
from .views.create import CreateCampaignView
from .views.detail import CampaignDetail
from .views.add_mechanic import AddMechanic
from .views.delete_mechanic import MechanicDelete
from .views.configuration import MappingView


app_name = 'campaign'

urlpatterns = [
    url(r'^$', login_required(CampaignList.as_view(), login_url='authentications:login'), name="campaign"),
    url(r'^inactive/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(inactive, login_url='authentications:login'),
        name="inactive-campaign"),
    url(r'^active/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(ActiveCampaign.as_view(), login_url='authentications:login'),
        name="activate-campaign"),
    url(r'^detail/(?P<campaign_id>[0-9A-Za-z]+)/$', login_required(CampaignDetail.as_view(), login_url='authentications:login'),
        name="campaign_detail"),
    url(r'^create$', login_required(CreateCampaignView.as_view(), login_url='authentications:login'),
        name="create_campaign"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/add_mechanic$', login_required(AddMechanic.as_view(), login_url='authentications:login'),
        name="add_mechanic"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/delete/(?P<mechanic_id>[0-9A-Za-z]+)/$', login_required(MechanicDelete.as_view(), login_url='authentications:login'),
        name="delete_mechanic"),
    url(r'^configuration/$', login_required(MappingView.as_view(), login_url='authentications:login'),
        name="campaign_configuration"),
]

