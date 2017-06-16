from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.cash_sof_list import CashSOFView
from .views.cash_transaction_list import CashTransactionView

app_name = 'cash_sofs'

urlpatterns = [
    url(r'^sofs/$', login_required(CashSOFView.as_view(), login_url='authentications:login'), name="cash_sof"),
    url(r'^transaction/$', login_required(CashTransactionView.as_view(), login_url='authentications:login'), name="cash_transaction"),
]
