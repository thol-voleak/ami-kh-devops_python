from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import RuleList
from .views.add_condition import AddRuleCondition


app_name = 'rule_configuration'

urlpatterns = [
    url(r'^$', login_required(RuleList.as_view(), login_url='authentications:login'), name="rule_engine"),
    url(r'^(?P<rule_id>[0-9A-Za-z]+)/(?P<mechanic_id>[0-9A-Za-z]+)/condition/$', login_required(AddRuleCondition.as_view(), login_url='authentications:login'),
        name="add_condition"),
]

