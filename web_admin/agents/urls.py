from .views.list import ListView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.registration import AgentRegistration
from .views.update import AgentUpdate

app_name = 'agents'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="agent-list"),
    url(r'^registration/$', login_required(AgentRegistration.as_view(), login_url='login'), name="agent_registration"),
    url(r'^update/$', login_required(AgentUpdate.as_view(), login_url='login'), name="agent_update"),
]
