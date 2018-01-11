from .views.list import ListView
from .views.agent_identities import AgentIdentitiesView
from .views.add_agent_identity import AddAgentIdentities
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.registration import AgentRegistration
from .views.update import AgentUpdate
from .views.detail import DetailView
from .views.delete import AgentDelete
from .views.reset_identity_password import reset_password
from .views.smart_card import SmartCardView
from .views.sof_cash import SOFCashView
from .views.sof_bank import SOFBankView
from .views.delete_smartcard import SmartCardDelete
from .views.suspend import suspend
from .views.activate import activate

app_name = 'agents'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="agent-list"),
    url(r'^registration/$', login_required(AgentRegistration.as_view(), login_url='authentications:login'), name="agent_registration"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="agent_detail"),
    url(r'^update/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(AgentUpdate.as_view(), login_url='authentications:login'), name="agent_update"),
    url(r'^delete/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(AgentDelete.as_view(), login_url='authentications:login'), name="agent_delete"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/identities/$', login_required(AgentIdentitiesView.as_view(), login_url='authentications:login'), name="agent_identities"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/identities/add/$', login_required(AddAgentIdentities.as_view(), login_url='authentications:login'), name="add_agent_identity"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/identities/(?P<identity_id>[0-9A-Za-z]+)/$', login_required(reset_password, login_url='authentications:login'), name="reset-identity-password"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/smardcards/$', login_required(SmartCardView.as_view(), login_url='authentications:login'), name="agent-smartcard"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/sofs/cash/$', login_required(SOFCashView.as_view(), login_url='authentications:login'), name="agent-sofcash"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/sofs/banks/$', login_required(SOFBankView.as_view(), login_url='authentications:login'), name="agent-sofbank"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/sofs/cash/$', login_required(SOFCashView.as_view(), login_url='authentications:login'), name="agent-add-sofcash"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/smardcards/(?P<smartcard_id>[0-9A-Za-z]+)$', login_required(SmartCardDelete.as_view(), login_url='authentications:login'), name="delete_agent_smartcard"),
    url(r'^suspend/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(suspend, login_url='authentications:login'), name="agent_suspend"),
    url(r'^activate/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(activate, login_url='authentications:login'), name="agent_activate"),
]