from .views.create import AgentTypeCreate
from .views.detail import DetailView
from .views.update import AgentTypeUpdateForm
from .views.delete import DeleteView
from .views.list import ListView

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'agent_type'

urlpatterns = [
    url(r'^create/$', login_required(AgentTypeCreate.as_view(), login_url='authentications:login'), name="create-agent-type"),
    url(r'^list/$', login_required(ListView.as_view(), login_url='authentications:login'), name="agent-type-list"),
    url(r'^detail/(?P<agentTypeId>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='authentications:login'),
        name="agent-type-detail"),
    url(r'^delete/(?P<agent_type_id>[0-9A-Za-z]+)/$', login_required(DeleteView.as_view(), login_url='authentications:login'),
        name="agent-type-delete"),
    url(r'^(?P<agent_type_id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'),
        name="delete-agent-type"),
    url(r'^update/(?P<agentTypeId>[0-9A-Za-z]+)/$', login_required(AgentTypeUpdateForm.as_view(), login_url='authentications:login'),
        name="agent-type-info"),
    url(r'^update-submit/(?P<agentTypeId>[0-9A-Za-z]+)/$',
        login_required(AgentTypeUpdateForm.as_view(), login_url='authentications:login'),
        name="agent-type-update"),
]
