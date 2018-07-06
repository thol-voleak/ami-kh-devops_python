import json
import logging
from authentications.utils import get_correlation_id_from_username
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin

from web_admin import api_settings
from web_admin import setup_logger, RestFulClient
from web_admin.utils import check_permissions

logger = logging.getLogger(__name__)

class RejectVoucherRefundView(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, 'CAN_APPROVE_VOUCHER_ADJUSTMENT')
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(RejectVoucherRefundView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start reject voucher refunds ==========')
        data = request.POST.copy()
        refundRequestIds = json.loads(data.get("refundRequestIds"))
        reason = data.get("reason")
        url = api_settings.VOUCHER_REFUND_APPROVE_PATH
        
        data = {
            "refund_request_ids": refundRequestIds,
            "reason": reason
        }
    
        is_success, status_code, status_message, data = RestFulClient.delete_return_data(
            url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=data
        )
        
        self.logger.info('========== Finish reject voucher refunds ==========')
        if is_success:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "System is processing, please wait a while"
            )

            return JsonResponse({
                "is_success": is_success
            })
        else:
            return JsonResponse({
                "is_success": is_success,
                "status_code": status_code,
                "status_message": status_message,
                "data": data
            })