from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from voucher.views.refund import VoucherRefundView, VoucherRefundRequestView
from .views.list import VoucherList
from .views.detail import VoucherDetail
from .views.transit import Transit
from .views.hold import HoldVoucher, UnholdVoucher


app_name = 'voucher'

urlpatterns = [
    url(r'^$', login_required(VoucherList.as_view(), login_url='authentications:login'), name="voucher"),
    url(r'^detail/(?P<voucher_id>[0-9A-Za-z]+)/$', login_required(VoucherDetail.as_view(), login_url='authentications:login'), name="voucher_detail"),
    url(r'^create/$', login_required(Transit.as_view(), login_url='authentications:login'), name="create_new_voucher"),
    url(r'^hold$', login_required(HoldVoucher.as_view(), login_url='authentications:login'), name="hold_voucher"),
    url(r'^unhold$', login_required(UnholdVoucher.as_view(), login_url='authentications:login'), name="unhold_voucher"),
    url(r'^refund', login_required(VoucherRefundView.as_view(), login_url='authentications:login'), name="refund"),
    url(r'^request/refund$', login_required(VoucherRefundRequestView.as_view(), login_url='authentications:login'), name="refund_request")
]