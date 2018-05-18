from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from campaign.views.add_action import AddAction
from campaign.views.add_condition import AddCondition
from .views.list import CampaignList
from .views.active import ActiveCampaign
from .views.inactive import inactive
from .views.create import CreateCampaignView
from .views.detail import CampaignDetail
from .views.add_mechanic import AddMechanic
from .views.delete_mechanic import MechanicDelete
from .views.delete_condition import ConditionDelete
from .views.delete_filter import FilterDelete
from .views.delete_action import ActionDelete
from .views.configuration import MappingView
from .views.amount_limit import AmountLimit
from .views.api_amount_limit import delete_amount_limit
from .views.mechanic_detail import MechanicDetail
from .views.edit_mechanic import EditMechanicView
from .views.delete_action_limit import DeleteActionLimitView

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
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/mechanics/(?P<mechanic_id>[0-9A-Za-z]+)/edit/$',
        login_required(EditMechanicView.as_view(), login_url='authentications:login'),
        name="edit_mechanic"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/delete/(?P<mechanic_id>[0-9A-Za-z]+)/$', login_required(MechanicDelete.as_view(), login_url='authentications:login'),
        name="delete_mechanic"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)/condition/(?P<condition_id>[0-9A-Za-z]+)/delete',
        login_required(ConditionDelete.as_view(), login_url='authentications:login'), name="delete_condition"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)/condition/(?P<condition_id>[0-9A-Za-z]+)/filter/(?P<filter_id>[0-9A-Za-z]+)/delete',
        login_required(FilterDelete.as_view(), login_url='authentications:login'), name="delete_filter"),
    url(r'^configuration/$', login_required(MappingView.as_view(), login_url='authentications:login'),
        name="campaign_configuration"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/amount-limit/$', login_required(AmountLimit.as_view(), login_url='authentications:login'),
        name="amount_limit"),
    url(r'^(?P<rule_id>[0-9A-Za-z]+)/amount-limit/(?P<rule_limit_id>[0-9A-Za-z]+)/delete', login_required(delete_amount_limit, login_url='authentications:login'),
        name="delete-amount-limit"),
    url(r'^detail/(?P<campaign_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)$', login_required(MechanicDetail.as_view(), login_url='authentications:login'),
        name="mechanic_detail"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)/add_condition$',
        login_required(AddCondition.as_view(), login_url='authentications:login'), name="add_condition"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)/add_action$',
        login_required(AddAction.as_view(), login_url='authentications:login'), name="add_action"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)/action/(?P<action_id>[0-9A-Za-z]+)/delete',
        login_required(ActionDelete.as_view(), login_url='authentications:login'), name="delete_action"),
    url(r'^(?P<campaign_id>[0-9A-Za-z]+)/mechanics/(?P<mechanic_id>[0-9A-Za-z]+)/actions/(?P<action_id>[0-9A-Za-z]+)/limits/(?P<action_limit_id>[0-9A-Za-z]+)/delete/$',
        login_required(DeleteActionLimitView.as_view(), login_url='authentications:login'), name="delete_action_limit"),
]

