from .views.list import ListView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.registration import AgentRegistration
from .views.update import AgentUpdate
from .views.detail import DetailView
from .views.delete import AgentDelete
from .views.delete_yes import AgentDeleteYes

app_name = 'agents'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="agent-list"),
    url(r'^registration/$', login_required(AgentRegistration.as_view(), login_url='login'), name="agent_registration"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='login'), name="agent_detail"),
    url(r'^update/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(AgentUpdate.as_view(), login_url='login'), name="agent_update"),
    url(r'^delete/(?P<agent_id>[0-9A-Za-z]+)/prev/(?P<prev_page>[0-9A-Za-z]+)/$', login_required(AgentDelete.as_view(), login_url='login'), name="agent_delete"),
    url(r'^delete_yes/(?P<agent_id>[0-9A-Za-z]+)/prev/(?P<prev_page>[0-9A-Za-z]+)/$', login_required(AgentDeleteYes.as_view(), login_url='login'), name="agent_delete_yes")
]
