from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import RuleList
from .views.add_condition import AddRuleCondition
from .views.create_rule import CreateRuleView
from .views.add_mechanic import AddMechanic
from .views.detail import RuleDetail
from .views.add_action import AddRuleAction


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
]
