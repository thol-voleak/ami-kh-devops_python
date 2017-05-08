from .views.list import ListView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.registration import AgentRegistration
from .views.detail import DetailView

app_name = 'agents'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="agent-list"),
    url(r'^registration/$', login_required(AgentRegistration.as_view(), login_url='login'), name="agent_registration"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='login'), name="agent_detail")
]
