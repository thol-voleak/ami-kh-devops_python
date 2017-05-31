from bank_sofs.views.list import BankSofsListView
from bank_sofs.views.create import BankSOFsCreateView

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'bank_sofs'

urlpatterns = [
    url(r'^bank/$', login_required(BankSofsListView.as_view(), login_url='login'), name="bank_sofs_list"),
    url(r'^bank/create$', login_required(BankSOFsCreateView.as_view(), login_url='login'), name="bank_sofs_create"),
]
