from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import RuleList


app_name = 'rule_configuration'

urlpatterns = [
    url(r'^$', login_required(RuleList.as_view(), login_url='authentications:login'), name="rule_engine"),
]

