from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from services.views.commision.agent_fee_distribution import (FeeDistributionsUpdate)
from services.views.tier.list import FeeTierListView
from services.views.tier.update import UpdateView as TierUpdateView
from services.views.tier.delete import TierDeleteView
from .views.commision.agent_bonus_distribution import (AgentFeeHierarchyDistributionsDetail)
from .views.command.delete import DeleteCommand
from .views.command.list import ListCommandView
from .views.tier.add import AddView
from .views.commision.commission_and_payment import (BalanceDistributionsUpdate,
                                           BonusDistributionsUpdate,
                                           CommissionAndPaymentView,
                                           PaymentAndFeeStructureDetailView,
                                           PaymentAndFeeStructureView,
                                           SettingBonusView,
                                           AgentBonusDistributionsUpdate,
                                           AgentFeeView,
                                           AgentBonusDistributions)
from .views.create import CreateView
from .views.commision.delete_agent_bonus import DeleteAgentBonus
from .views.commision.delete_setting_bonus import DeleteSettingBonus
from .views.detail import ServiceDetailForm
from .views.services_list import ListView
from .views.update import UpdateView
from .views.delete import ServiceDeleteForm
from .views.spi.list import SPIView
from .views.spi.update import SPIUpdate
from .views.spi.delete import SPIDeleteView

app_name = "services"

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="services_list"),
    url(r'^details/(?P<ServiceId>[0-9A-Za-z]+)/$', login_required(ServiceDetailForm.as_view(), login_url='authentications:login'),
        name="service_detail"),
    url(r'^add/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="service_create"),
    url(r'^update/(?P<service_id>[0-9A-Za-z]+)/$', login_required(UpdateView.as_view(), login_url='authentications:login'),
        name="update_service"),
    url(r'^delete/(?P<ServiceId>[0-9A-Za-z]+)/$', login_required(ServiceDeleteForm.as_view(), login_url='authentications:login'),
        name="delete_service"),
    url(r'^(?P<service_id>[0-9A-Za-z]+)/commands/$', login_required(ListCommandView.as_view(), login_url='authentications:login'),
        name="command_list"),
    url(r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<service_command_id>[0-9A-Za-z]+)$',
        login_required(DeleteCommand.as_view(), login_url='authentications:login'),
        name="command_delete"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/$',
        login_required(FeeTierListView.as_view(), login_url='authentications:login'),
        name="fee_tier_list"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/add/$',
        login_required(AddView.as_view(), login_url='authentications:login'),
        name="add_tier"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/$',
        login_required(CommissionAndPaymentView.as_view(), login_url='authentications:login'),
        name="commission_and_payment"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/payment-and-fee-structure/$',
        login_required(PaymentAndFeeStructureView.as_view(), login_url='authentications:login'),
        name="payment_and_fee_stucture"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/setting-bonus/$',
        login_required(SettingBonusView.as_view(), login_url='authentications:login'),
        name="setting_bonus"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/payment-and-fee-structure/(?P<balance_distribution_id>[0-9A-Za-z]+)/$',
        login_required(PaymentAndFeeStructureDetailView.as_view(), login_url='authentications:login'),
        name="payment_and_fee_stucture_detail"),
    url(r'^balance-distributions/(?P<balance_distributions_id>[0-9A-Za-z]+)/$',
        login_required(BalanceDistributionsUpdate.as_view(), login_url='authentications:login'),
        name="payment_and_fee_stucture_update"),
    url(r'^bonus-distributions/(?P<bonus_distributions_id>[0-9A-Za-z]+)/$',
        login_required(BonusDistributionsUpdate.as_view(), login_url='authentications:login'),
        name="setting_bonus_update"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/agent-bonus-distributions/$',
        login_required(AgentBonusDistributions.as_view(), login_url='authentications:login'),
        name="agent_bonus_distribution"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/update/$',
        login_required(TierUpdateView.as_view(), login_url='authentications:login'),
        name="update_tier"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/delete/$',
        login_required(TierDeleteView.as_view(), login_url='authentications:login'),
        name="delete_tier"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/setting-bonus/(?P<bonus_distribution_id>[0-9A-Za-z]+)/$',
        login_required(DeleteSettingBonus.as_view(), login_url='authentications:login'),
        name="delete_setting_bonus"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/agent-fee/$',
        login_required(AgentFeeView.as_view(), login_url='authentications:login'),
        name="agent_fee"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/agent-fee/(?P<agent_fee_distribution_id>[0-9A-Za-z]+)/$',
        login_required(AgentFeeHierarchyDistributionsDetail.as_view(), login_url='authentications:login'),
        name="agent_fee_distribution_detail"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/agent-bonus-distributions/(?P<agent_bonus_distribution_id>[0-9A-Za-z]+)/$',
        login_required(DeleteAgentBonus.as_view(), login_url='authentications:login'),
        name="delete_agent_bonus_distribution"),
    url(r'^fee-distribution/(?P<fee_distributions_id>[0-9A-Za-z]+)/$',
        login_required(FeeDistributionsUpdate.as_view(), login_url='authentications:login'),
        name="agent_fee_update"),
    url(r'^agent-bonus-distributions/(?P<agent_bonus_distribution_id>[0-9A-Za-z]+)/$',
        login_required(AgentBonusDistributionsUpdate.as_view(), login_url='authentications:login'),
        name="agent_bonus_distributions_update"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/spi-urls/$',
        login_required(SPIView.as_view(), login_url='authentications:login'),
        name="spi_list"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/spi-urls/(?P<spiUrlId>[0-9A-Za-z]+)$',
        login_required(SPIUpdate.as_view(), login_url='authentications:login'),
        name="spi_update"),
    url(
        r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/spi-urls/(?P<spi_url_id>[0-9A-Za-z]+)/delete/$',
        login_required(SPIDeleteView.as_view(), login_url='authentications:login'),
        name="spi-delete"),
]
