from card_sofs.views.sof.bank_sof_list import BankSOFView

from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'card_sofs'

urlpatterns = [
    url(r'^sofs/$', login_required(BankSOFView.as_view(), login_url='authentications:login'), name="card_sof")
]
