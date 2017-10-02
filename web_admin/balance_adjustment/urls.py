from balance_adjustment.views.list import BalanceAdjustmentListView

from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'balance_adjustment'

urlpatterns = [
    url(r'^requests/$', login_required(BalanceAdjustmentListView.as_view(), login_url='authentications:login'), name="balance_adjustment_list"),
]
