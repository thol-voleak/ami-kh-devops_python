from balance_adjustment.views.list import (BalanceAdjustmentListView, BalanceAdjustmentListActionView)
from balance_adjustment.views.create import BalanceAdjustmentCreateView
from balance_adjustment.views.detail import BalanceAdjustmentDetailView

from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'balance_adjustment'

urlpatterns = [
    url(r'^requests/$', login_required(BalanceAdjustmentListView.as_view(), login_url='authentications:login'), name="balance_adjustment_list"),
    url(r'^execute/$', login_required(BalanceAdjustmentCreateView.as_view(), login_url='authentications:login'), name="balance_adjustment_create"),
    url(r'^details/(?P<ReferenceId>[0-9A-Za-z]+)/$', login_required(BalanceAdjustmentDetailView.as_view(), login_url='authentications:login'), name="balance_adjustment_detail"),
    url(r'^approve/(?P<OrderId>[0-9A-Za-z]+)/$', login_required(BalanceAdjustmentDetailView.as_view(), login_url='authentications:login'), name="balance_adjustment_approve"),

    url(r'^process_multi_balance_adjustment/$', login_required(BalanceAdjustmentListActionView.as_view(), login_url='authentications:login'), name="process_multi_balance_adjustments"),
]
