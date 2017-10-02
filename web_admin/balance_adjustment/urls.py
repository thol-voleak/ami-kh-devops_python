from balance_adjustment.views.list import BalanceAdjustmentListView
from balance_adjustment.views.create import BalanceAdjustmentCreateView

from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'balance_adjustment'

urlpatterns = [
    url(r'^requests/$', login_required(BalanceAdjustmentListView.as_view(), login_url='authentications:login'), name="balance_adjustment_list"),
    url(r'^execute/$', login_required(BalanceAdjustmentCreateView.as_view(), login_url='authentications:login'), name="balance_adjustment_create"),
]
