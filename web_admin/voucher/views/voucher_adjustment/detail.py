import logging
from authentications.utils import get_correlation_id_from_username
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.global_constants import REFUND_STATUS
from web_admin.restful_client import RestFulClient

from web_admin import setup_logger, api_settings

logger = logging.getLogger(__name__)


class VoucherAdjustmentDetailView(TemplateView, GetHeaderMixin):
    template_name = "voucher_adjustment/detail.html"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        # TODO check permision to view voucher refund detail
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(VoucherAdjustmentDetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start render Vouchers Adjustment detail page==========')
        context = super(VoucherAdjustmentDetailView, self).get_context_data(**kwargs)
        voucher_refund_id = context["voucher_refund_id"]
        voucherRefundDetail = self._get_voucher_refund_detail(voucher_refund_id)
        oldVoucherDetail = None
        if voucherRefundDetail is not None:
            self._format_data(voucherRefundDetail)
            oldVoucherDetail = self._get_voucher_detail(voucherRefundDetail.get("voucher_id"))

        context = {
            'voucherRefundDetail': voucherRefundDetail,
            'oldVoucherDetail': oldVoucherDetail
        }
        self.logger.info('========== Finish render Vouchers Adjustment detail page==========')
        return render(request, self.template_name, context)

    def _format_data(self, voucherRefund):
        voucherRefund['status'] = REFUND_STATUS.get(str(voucherRefund.get('status_id')))
        return voucherRefund

    def _get_voucher_refund_detail(self, id):
        url = api_settings.SEARCH_VOUCHER_ADJUSTMENT
        params = {
            'id': id
        }
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            return None
        if len(data['refund_vouchers']) == 0:
            return None
        else:
            return data['refund_vouchers'][0]

    def _get_voucher_detail(self, id_of_voucher):
        url = api_settings.GET_VOUCHER_DETAIL
        params = {
            'id': id_of_voucher
        }
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            return None
        if len(data['vouchers']) == 0:
            return None
        else:
            return data['vouchers'][0]
