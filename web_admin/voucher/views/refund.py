from django.contrib import messages
from django.http import HttpResponse

from authentications.utils import get_correlation_id_from_username
from web_admin import settings
from web_admin import setup_logger, RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.api_settings import GET_VOUCHER_DETAIL
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import check_permissions
import json
from web_admin import api_settings
from django.http import JsonResponse

from django.views.generic.base import TemplateView
import logging

logger = logging.getLogger(__name__)


class VoucherRefundView(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        # check_permissions(request, "CAN_REFUND_VOUCHER")
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(VoucherRefundView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start get Vouchers refund information ==========')
        # context = super(VoucherRefundView, self).get_context_data(**kwargs)
        voucher_id = request.POST.get('voucher_id')
        data = self._get_voucher_detail(voucher_id)
        self.logger.info('========== Fisnish get Vouchers details ==========')
        return JsonResponse({ "data": data  })

    def _get_voucher_detail(self, voucher_id):
        url = GET_VOUCHER_DETAIL
        params = {
            'voucher_id': voucher_id
        }
        is_success, status_code, status_message, data= RestFulClient.post(url=url,
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
            data = []
        data = data['vouchers']
        if data[0]["is_cancelled"]:
            data = [{'id': -1, "code": "voucher_was_cancelled"}]
        return data