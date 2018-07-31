from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from voucher.views.refund import VoucherRefundView, VoucherRefundRequestView
from voucher.views.third_party_voucher_upload import upload_form, upload_progress

from voucher.views.cancel import VoucherCancelView
from .views.list import VoucherList
from .views.detail import VoucherDetail
from .views.transit import Transit
from .views.hold import HoldVoucher, UnholdVoucher
from .views.approve_voucher_refund import ApproveVoucherRefundView
from .views.reject_voucher_refund import RejectVoucherRefundView
from voucher.views.adjustment import VoucherAdjustmentList
from voucher.views.voucher_adjustment.detail import VoucherAdjustmentDetailView
from voucher.views.voucher_adjustment.approve_voucher_cancel import ApproveVoucherCancelView


app_name = 'voucher'

urlpatterns = [
    url(r'^$', login_required(VoucherList.as_view(), login_url='authentications:login'), name="voucher"),
    url(r'^detail/(?P<voucher_id>[0-9A-Za-z_@!#]+)/$', login_required(VoucherDetail.as_view(), login_url='authentications:login'), name="voucher_detail"),
    url(r'^create/$', login_required(Transit.as_view(), login_url='authentications:login'), name="create_new_voucher"),
    url(r'^hold$', login_required(HoldVoucher.as_view(), login_url='authentications:login'), name="hold_voucher"),
    url(r'^unhold$', login_required(UnholdVoucher.as_view(), login_url='authentications:login'), name="unhold_voucher"),
    url(r'^refund', login_required(VoucherRefundView.as_view(), login_url='authentications:login'), name="refund"),
    url(r'^request/refund$', login_required(VoucherRefundRequestView.as_view(), login_url='authentications:login'), name="refund_request"),
    url(r'^approve_voucher_refunds$', login_required(ApproveVoucherRefundView.as_view(), login_url='authentications:login'), name="approve_voucher_refunds"),
    url(r'^reject_voucher_refunds$', login_required(RejectVoucherRefundView.as_view(), login_url='authentications:login'), name="reject_voucher_refunds"),
    url(r'^adjustment$', login_required(VoucherAdjustmentList.as_view(), login_url='authentications:login'), name="voucher_adjustment"),
    url(r'^adjustment/detail/(?P<voucher_refund_id>[0-9]+)/$', login_required(VoucherAdjustmentDetailView.as_view(), login_url='authentications:login'), name="voucher_adjustment_detail"),
    url(r'^upload/$', login_required(upload_form, login_url='authentications:login'), name="upload"),
    url(r'^upload_progress/$', login_required(upload_progress, login_url='authentications:login'),name="upload_progress"),
    url(r'^cancel', login_required(VoucherCancelView.as_view(), login_url='authentications:login'), name="cancel"),
    url(r'^approve_voucher_cancels$', login_required(ApproveVoucherCancelView.as_view(), login_url='authentications:login'), name="approve_voucher_cancels"),
]