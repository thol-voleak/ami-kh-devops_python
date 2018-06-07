"""web_admin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from authentications.views.auth import logout_user
from web.views import health
from web.views import backlog

urlpatterns = [
    # url(r'^admin-portal/login/$', auth_views.login, {'template_name': 'authentications/login.html'}, name='login'),
    url(r'^admin-portal/', include('web.urls')),
    url(r'^admin-portal/authentications/', include('authentications.urls')),
    url(r'^admin-portal/clients/', include('clients.urls')),
    url(r'^admin-portal/password-center/', include('password_center.urls')),
    url(r'^admin-portal/balances/', include('balances.urls')),
    url(r'^admin-portal/health$', health, name="health"),
    url(r'^admin-portal/backlog/$', backlog, name="backlog"),
    url(r'^admin-portal/logout/$', logout_user, name='logout'),
    url(r'^admin-portal/agent-type/', include('agent_type.urls')),
    url(r'^admin-portal/system-user/', include('system_user.urls')),
    url(r'^admin-portal/service-group/', include('service_group.urls')),
    url(r'^admin-portal/services/', include('services.urls')),
    url(r'^admin-portal/agents/', include('agents.urls')),
    url(r'^admin-portal/customers/', include('customers.urls')),
    url(r'^admin-portal/cards/', include('cards.urls')),
    url(r'^admin-portal/card-type/', include('card_type.urls')),
    url(r'^admin-portal/cash/', include('cash_sofs.urls')),
    url(r'^admin-portal/payments/', include('payments.urls')),
    url(r'^admin-portal/api-management/', include('api_management.urls')),
    url(r'^admin-portal/centralize-configuration/', include('centralize_configuration.urls')),
    url(r'^admin-portal/bank-sof/', include('bank_sofs.urls')),
    url(r'^admin-portal/bank/', include('bank.urls')),
    url(r'^admin-portal/reconcile/', include('reconcile.urls')),
    url(r'^admin-portal/card-designs/', include('card_design.urls')),
    url(r'^admin-portal/card-provider/', include('card_provider.urls')),
    url(r'^admin-portal/card-sofs/', include('card_sofs.urls')),
    url(r'^admin-portal/balance-adjustment/', include('balance_adjustment.urls')),
    url(r'^admin-portal/campaign/', include('campaign.urls')),
    url(r'^admin-portal/fraud-prevention/', include('fraud_prevention.urls')),
    url(r'^admin-portal/rule-configuration/', include('rule_configuration.urls')),
    url(r'^admin-portal/voucher/', include('voucher.urls')),
    url(r'^admin-portal/report-configuration/', include('report_configuration.urls')),
    url(r'^admin-portal/category/', include('category.urls')),
    url(r'^admin-portal/product/', include('product.urls')),
    url(r'^admin-portal/shop-types/', include('shop_type.urls')),
    url(r'^admin-portal/shop-categories/', include('shop_category.urls')),
    url(r'^admin-portal/shops/', include('shop.urls')),
    url(r'^admin-portal/channel-gateway/services/', include('channel_gateway.service.urls')),
    url(r'^admin-portal/channel-gateway/apis/', include('channel_gateway.api.urls')),
    url(r'^admin-portal/uploads/', include('upload_management.urls')),
    url(r'^admin-portal/otp/', include('authentications.one_time_password_report.urls')),
]
