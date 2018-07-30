import json

from authentications.utils import get_correlation_id_from_username
from web_admin import settings
from web_admin import setup_logger, RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.api_settings import CREATE_CANCEL_REQUEST, CONFIRM_CANCEL_REQUEST, ORDER_BAL_ADJUST_PATH
from web_admin.get_header_mixins import GetHeaderMixin
from django.http import JsonResponse

from django.views.generic.base import TemplateView
import logging

logger = logging.getLogger(__name__)


class VoucherCancelView(TemplateView, GetHeaderMixin):
    logger = logger
    
    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(VoucherCancelView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.logger.info("request: " + format(request.POST));
        product_service_id = request.POST.get('product_service_id')
        product_ref1 = request.POST.get('product_ref1')
        product_ref2 = request.POST.get('product_ref2')
        product_ref3 = request.POST.get('product_ref3')
        product_ref4 = request.POST.get('product_ref4')
        product_ref5 = request.POST.get('product_ref5')
        reason_for_cancel = request.POST.get('reason_for_cancel')
        vouchers = json.loads(request.POST.get('vouchers'))
        
        initiator_user_id = request.POST.get('initiator_user_id')
        initiator_sof_id = request.POST.get('initiator_sof_id')
        
        payer_user_id = request.POST.get('issuer_user_id')
        payer_user_type_id = request.POST.get('issuer_user_type_id')
        payer_user_type_name = request.POST.get('issuer_user_type_name')
        payer_sof_id = request.POST.get('issuer_sof_id')
        payer_sof_type_id = request.POST.get('issuer_sof_type_id')
        
        payee_user_id = request.POST.get('payee_user_id')
        payee_sof_id = request.POST.get('payee_sof_id')
        
        currency = request.POST.get('currency')
        amount = request.POST.get('total_amount')

        voucher_cancel_request = {
            "currency": currency,
            "reason_for_cancellation": reason_for_cancel,
            "vouchers": vouchers
        }
        response = self._create_cancel_request(voucher_cancel_request)
        content = json.loads(response.content)
        self.logger.info("response: " + format(content))
        if not content['is_success']:
            return JsonResponse({
                "status_code": content['status_code'],
                "status_message": content['status_message']
            })
        
        voucher_cancel_id = content['data']['voucher_cancellation_id']
        response = self._confirm_cancel_request(voucher_cancel_id)
        content = json.loads(response.content)
        self.logger.info("response: " + format(content))
        if not content['is_success']:
            return JsonResponse({
                "status_code": content['status_code'],
                "status_message": content['status_message']
            })
        
        balance_adjustment_request = {
            "product_service_id": product_service_id,
            "amount": amount,
            "product": {
                "product_ref1": product_ref1,
                "product_ref2": product_ref2,
                "product_ref3": product_ref3,
                "product_ref4": product_ref4,
                "product_ref5": product_ref5
            },
            "initiator":{
                "user_id": initiator_user_id,
                "user_type": {
                    "id": 2,
                    "name": "agent"
                },
                "sof":{
                    "id": initiator_sof_id,
                    "type_id": 2
                }
            },
            "payer_user": {
                "user_id": payer_user_id,
                "user_type": {
                    "id": payer_user_type_id,
                    "name": payer_user_type_name
                },
                "sof": {
                    "id": payer_sof_id,
                    "type_id": payer_sof_type_id
                }
            },
            "payee_user": {
                "user_id": payee_user_id,
                "user_type": {
                    "id": 2,
                    "name": "agent"
                },
                "sof": {
                    "id": payee_sof_id,
                    "type_id": 2
                }
            },
            "cancel_ref_id": voucher_cancel_id,
            "reason": reason_for_cancel
        }
        response = self._create_balance_adjustment_order(balance_adjustment_request)
        content = json.loads(response.content)
        self.logger.info("response: " + format(content))
        if not content['is_success']:
            return JsonResponse({
                "status_code": content['status_code'],
                "status_message": content['status_message']
            })
            
        return JsonResponse({
            "status_code": content['status_code'],
            "status_message": content['status_message'],
            "voucher_cancel_id": voucher_cancel_id,
            "reference_id": content['data']['reference_id']
        })


    def _create_cancel_request(self, voucher_cancel_request):
        self.logger.info('========== Start create voucher cancel request ==========')
        url = CREATE_CANCEL_REQUEST
        params = voucher_cancel_request
        self.logger.info("voucher_cancel_request: " + format(voucher_cancel_request));
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        
        if not is_success:
            data = []
            
        self.logger.info('========== Finish create voucher cancel request ==========')
        return JsonResponse({
            "is_success": is_success,
            "status_code": status_code,
            "status_message": status_message,
            "data": data
        })


    def _confirm_cancel_request(self, voucher_cancel_id):
        self.logger.info('========== Start confirm cancel request ==========')
        url = CONFIRM_CANCEL_REQUEST.format(id=voucher_cancel_id)
        is_success, status_code, status_message, data = RestFulClient.put(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        
        API_Logger.post_logging(loggers=self.logger, response=data,
                                status_code=status_code)

        self.logger.info('========== Finish confirm cancel request ==========')
        return JsonResponse({
            "is_success": is_success,
            "status_code": status_code,
            "status_message": status_message,
            "data": data
        })


    def _create_balance_adjustment_order(self, balance_adjustment_request):
        self.logger.info('========== Start create balance adjustment order ==========')
        url = ORDER_BAL_ADJUST_PATH
        params = balance_adjustment_request
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                          headers=self._get_headers(),
                                                                          loggers=self.logger,
                                                                          params=params,
                                                                          timeout=settings.GLOBAL_TIMEOUT)
        
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish create balance adjustment order ==========')
        return JsonResponse({
                    "is_success": is_success,
                    "status_code": status_code,
                    "status_message": status_message,
                    "data": data
                })
