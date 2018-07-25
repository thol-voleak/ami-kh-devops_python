from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.cash_sof_list import CashSOFView, CashSofJsonView
from .views.cash_transaction_list import CashTransactionView
from .views.user_list import UserList

app_name = 'cash_sofs'

urlpatterns = [
    url(r'^sofs/$', login_required(CashSOFView.as_view(), login_url='authentications:login'), name="cash_sof"),
    url(r'^transaction/$', login_required(CashTransactionView.as_view(), login_url='authentications:login'), name="cash_transaction"),
    url(r'^users/$', login_required(UserList.as_view(), login_url='authentications:login'), name="search_user"),
    url(r'^sofs/json/$', login_required(CashSofJsonView.as_view(), login_url='authentications:login'), name="cash_sof_json"),
]
