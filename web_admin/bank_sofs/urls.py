from bank_sofs.views.list import BankSofsListView
from bank_sofs.views.create import BankSOFsCreateView
from bank_sofs.views.edit import BankSOFsUpdateView

from bank_sofs.views.detail import BankSOFsDetailView
from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'bank_sofs'

urlpatterns = [
    url(r'^bank/$', login_required(BankSofsListView.as_view(), login_url='login'), name="bank_sofs_list"),
    url(r'^bank/create$', login_required(BankSOFsCreateView.as_view(), login_url='login'), name="bank_sofs_create"),
    url(r'^bank/(?P<bank_id>[0-9A-Za-z]+)/edit$', login_required(BankSOFsUpdateView.as_view(), login_url='login'), name="bank_sofs_edit"),
    url(r'^bank/(?P<bank_id>[0-9A-Za-z]+)/detail$', login_required(BankSOFsDetailView.as_view(), login_url='login'), name="bank_sofs_detail"),
]
