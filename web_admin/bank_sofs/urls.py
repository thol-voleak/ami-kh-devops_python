from bank_sofs.views.bank.create import CreateView
from bank_sofs.views.bank.delete import DeleteView
from bank_sofs.views.bank.edit import EditView
from bank_sofs.views.bank.list import ListView
from bank_sofs.views.sof.bank_sof_list import BankSOFView
from bank_sofs.views.sof.bank_sof_transaction import BankSOFTransaction

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from bank_sofs.views.bank.detail import DetailsView

app_name = 'bank_sofs'

urlpatterns = [
    url(r'^management/$', login_required(ListView.as_view(), login_url='login'), name="bank_sofs_list"),
    url(r'^sofs/$', login_required(BankSOFView.as_view(), login_url='login'), name="bank_sof"),
    url(r'^sofs/create/$', login_required(CreateView.as_view(), login_url='login'), name="bank_sofs_create"),
    url(r'^sofs/(?P<bank_id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='login'), name="bank_sofs_edit"),
    url(r'^sofs/(?P<bank_id>[0-9A-Za-z]+)/detail/$', login_required(DetailsView.as_view(), login_url='login'), name="bank_sofs_detail"),
    url(r'^sofs/(?P<bank_id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='login'), name="bank_sofs_delete"),
    url(r'^sofs/transaction/$', login_required(BankSOFTransaction.as_view(), login_url='login'), name="bank_sofs_transaction"),
]
