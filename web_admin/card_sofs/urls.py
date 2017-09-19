from card_sofs.views.card_sof_list import CardSOFView
from card_sofs.views.card_sof_transaction import CardSOFTransaction

from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'card_sofs'

urlpatterns = [
    url(r'^sofs/$', login_required(CardSOFView.as_view(), login_url='authentications:login'), name="card_sof"),
    url(r'^sofs/transaction/$', login_required(CardSOFTransaction.as_view(), login_url='authentications:login'), name="card_sofs_transaction")
]
