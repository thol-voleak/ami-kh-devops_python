from . import views
from .views.create import AgentTypeCreate
from .views.detail import DetailView
from .views.delete import DeleteView
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.delete import delete_agent_type
# from .api import ClientApi

app_name = 'agent_type'

urlpatterns = [

    # url(r'^$', views.create.index, name='index'),
    url(r'^create/$', login_required(AgentTypeCreate.as_view(), login_url='login'), name="create-agent-type"),
    url(r'^list/$', login_required(ListView.as_view(), login_url='login'), name="agent-type-list"),
    url(r'^detail/(?P<agentTypeId>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='login'),
        name="agent-type-detail"),
    url(r'^delete/(?P<agent_type_id>[0-9A-Za-z]+)/$', login_required(DeleteView.as_view(), login_url='login'),
        name="agent-type-delete"),
    url(r'^(?P<agent_type_id>[0-9A-Za-z]+)/delete/$', login_required(delete_agent_type, login_url='login'),
        name="delete-agent-type"),

]
