from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import RuleList
from .views.add_condition import AddRuleCondition
from .views.create_rule import CreateRuleView
from .views.add_mechanic import AddMechanic
from .views.detail import RuleDetail
from .views.add_action import AddRuleAction
from .views.active import ActiveRule
from .views.inactive import InactiveRule
from .views.delete_mechanic import MechanicDelete

app_name = 'rule_configuration'

urlpatterns = [
    url(r'^$', login_required(RuleList.as_view(), login_url='authentications:login'), name="rule_engine"),
    url(r'^(?P<rule_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)/condition/create$', login_required(AddRuleCondition.as_view(), login_url='authentications:login'),
        name="add_condition"),
    url(r'^(?P<rule_id>[0-9A-Za-z]+)/mechanic/create$', login_required(AddMechanic.as_view(), login_url='authentications:login'),
        name="add_mechanics"),
    url(r'^create$', login_required(CreateRuleView.as_view(), login_url='authentications:login'),
        name="create_rule"),
    url(r'^detail/(?P<rule_id>[0-9A-Za-z]+)/$', login_required(RuleDetail.as_view(), login_url='authentications:login'),
        name="rule_detail"),
    url(r'^(?P<rule_id>[0-9A-Za-z]+)/mechanic/(?P<mechanic_id>[0-9A-Za-z]+)/action/create$',
        login_required(AddRuleAction.as_view(), login_url='authentications:login'),
        name="add_action"),
    url(r'^inactive/(?P<rule_id>[0-9A-Za-z]+)/$', login_required(InactiveRule.as_view(), login_url='authentications:login'),
        name="inactive-rule"),
    url(r'^active/(?P<rule_id>[0-9A-Za-z]+)/$', login_required(ActiveRule.as_view(), login_url='authentications:login'),
        name="activate-rule"),
    url(r'^(?P<rule_id>[0-9A-Za-z]+)/delete/(?P<mechanic_id>[0-9A-Za-z]+)/$', login_required(MechanicDelete.as_view(), login_url='authentications:login'),
        name="delete_rule_mechanic"),
]
