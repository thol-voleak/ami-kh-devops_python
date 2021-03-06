from agents.views.agent_link_shop import AgentLinkShop
from agents.views.management_shop import AgentManagementShop
from .views.list import ListView
from .views.agent_identities import AgentIdentitiesView
from .views.add_agent_identity import AddAgentIdentities
from .views.transaction_history import TransactionHistoryView
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
from .views.management_summary import AgentManagementSummary
from .views.management_relationship import AgentManagementRelationship
from .views.management_product import AgentManagementProduct
from .views.link_agent_to_shop import LinkAgentToShop
from .views.unlink_shop_from_agent import UnLinkAgentToShop
from .views.relationship_ajax_action import delete_relationship, share_benefit_relationship
from .views.relationship_ajax_action import stop_share_benefit_relationship
from .views.relationship_ajax_action import add_agent_relationship

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
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/transaction-histories/$', login_required(TransactionHistoryView.as_view(), login_url='authentications:login'), name="agent_transaction_history"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/smardcards/$', login_required(SmartCardView.as_view(), login_url='authentications:login'), name="agent-smartcard"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/sofs/cash/$', login_required(SOFCashView.as_view(), login_url='authentications:login'), name="agent-sofcash"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/sofs/banks/$', login_required(SOFBankView.as_view(), login_url='authentications:login'), name="agent-sofbank"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/sofs/cash/$', login_required(SOFCashView.as_view(), login_url='authentications:login'), name="agent-add-sofcash"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/smardcards/(?P<smartcard_id>[0-9A-Za-z]+)$', login_required(SmartCardDelete.as_view(), login_url='authentications:login'), name="delete_agent_smartcard"),
    url(r'^suspend/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(suspend, login_url='authentications:login'), name="agent_suspend"),
    url(r'^activate/(?P<agent_id>[0-9A-Za-z]+)/$', login_required(activate, login_url='authentications:login'), name="agent_activate"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/management/summary$', login_required(AgentManagementSummary.as_view(), login_url='authentications:login'), name="agent_management_summary"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/management/relationship', login_required(AgentManagementRelationship.as_view(), login_url='authentications:login'), name="agent_management_relationship"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/management/product', login_required(AgentManagementProduct.as_view(), login_url='authentications:login'), name="agent_management_product"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/management/shop', login_required(AgentManagementShop.as_view(), login_url='authentications:login'), name="agent_management_shop"),
    url(r'^relationships/delete/(?P<relationship_id>[0-9A-Za-z]+)$', login_required(delete_relationship, login_url='authentications:login'), name="relationship_delete"),
    url(r'^relationships/share-benefit/(?P<relationship_id>[0-9A-Za-z]+)$', login_required(share_benefit_relationship, login_url='authentications:login'), name="share_benefit_relationship"),
    url(r'^relationships/stop-share-benefit/(?P<relationship_id>[0-9A-Za-z]+)$', login_required(stop_share_benefit_relationship, login_url='authentications:login'), name="stop_share_benefit_relationship"),
    url(r'^relationships/add/(?P<agent_id>[0-9A-Za-z]+)',login_required(add_agent_relationship, login_url='authentications:login'),name="add_agent_relationship"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/link-shop', login_required(AgentLinkShop.as_view(), login_url='authentications:login'), name="agent_link_shop"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/shop/(?P<shop_id>[0-9A-Za-z]+)/link',
        login_required(LinkAgentToShop.as_view(), login_url='authentications:login'), name="link_agent_shop"),
    url(r'^(?P<agent_id>[0-9A-Za-z]+)/shop/(?P<shop_id>[0-9A-Za-z]+)/unlink',
        login_required(UnLinkAgentToShop.as_view(), login_url='authentications:login'), name="unlink_agent_shop"),
]