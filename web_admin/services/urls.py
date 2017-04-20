from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views.command.list import ListCommandView
from .views.command.tier.add import AddView
from .views.commission_and_payment import CommissionAndPaymentView
from .views.create import CreateView
from .views.detail import ServiceDetailForm
from .views.fee_tier import FeeTierListView
from .views.services_list import ListView
from .views.update import UpdateView

app_name = "services"

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="services_list"),
    url(r'^details/(?P<ServiceId>[0-9A-Za-z]+)/$', login_required(ServiceDetailForm.as_view(), login_url='login'),
        name="service_detail"),
    url(r'^add/$', login_required(CreateView.as_view(), login_url='login'), name="service_create"),
    url(r'^update/(?P<service_id>[0-9A-Za-z]+)/$', login_required(UpdateView.as_view(), login_url='login'),
        name="update_service"),
    url(r'^(?P<service_id>[0-9A-Za-z]+)/commands/$', login_required(ListCommandView.as_view(), login_url='login'),
        name="command_list"),
    url(r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/$',
        login_required(FeeTierListView.as_view(), login_url='login'),
        name="fee_tier_list"),
    url(r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/add/$',
        login_required(AddView.as_view(), login_url='login'),
        name="add_tier"),
    url(r'^(?P<service_id>[0-9A-Za-z]+)/commands/(?P<command_id>[0-9A-Za-z]+)/service-command/(?P<service_command_id>[0-9A-Za-z]+)/tiers/(?P<fee_tier_id>[0-9A-Za-z]+)/commission-and-payment/$',
        login_required(CommissionAndPaymentView.as_view(), login_url='login'),
        name="commission_and_payment"),
]
