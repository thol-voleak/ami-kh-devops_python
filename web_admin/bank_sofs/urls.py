from bank_sofs.views.sof.bank_sof_list import BankSOFView
from bank_sofs.views.sof.bank_sof_transaction import BankSOFTransaction

from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'bank_sofs'

urlpatterns = [
    url(r'^sofs/$', login_required(BankSOFView.as_view(), login_url='authentications:login'), name="bank_sof"),
    url(r'^sofs/transaction/$', login_required(BankSOFTransaction.as_view(), login_url='authentications:login'), name="bank_sofs_transaction"),
]