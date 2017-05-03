from . import views
from .views.create import AgentTypeCreate
from .views.detail import DetailView
from .views.update import AgentTypeUpdateForm
from .views.update import AgentTypeUpdate

from .views.delete import DeleteView
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.delete import delete_agent_type
# from .api import ClientApi

app_name = 'agents'

urlpatterns = [


]

