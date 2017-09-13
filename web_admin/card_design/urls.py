from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import CardDesignList
# from .views.update import AgentUpdate
# from .views.detail import DetailView
# from .views.delete import AgentDelete

app_name = 'card_design'

urlpatterns = [
    url(r'^$', login_required(CardDesignList.as_view(), login_url='authentications:login'), name="card_designs"),
    # url(r'^registration/$', login_required(AgentRegistration.as_view(), login_url='authentications:login'), name="agent_registration"),
    # url(r'^(?P<agent_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="agent_detail"),
    # url(r'^update/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(AgentUpdate.as_view(), login_url='authentications:login'), name="agent_update"),
    # url(r'^delete/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(AgentDelete.as_view(), login_url='authentications:login'), name="agent_delete")
]