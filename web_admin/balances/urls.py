from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .api import BalanceApi

from balances.views.company_balance import CompanyBalanceView
app_name = 'balances'

urlpatterns = [
    url(r'^currencies/$', login_required(ListView.as_view(), login_url='login'), name="currency-list"),
    url(r'^currencies/(?P<currency>[A-Za-z]+)/add/$', login_required(BalanceApi.add, login_url='login'),
        name="currency-add"),
    url(r'^company-balance/$', login_required(CompanyBalanceView.as_view(), login_url='login'),
        name="setup_company_balance"),
]
