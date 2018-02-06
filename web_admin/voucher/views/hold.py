from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from web_admin import setup_logger, RestFulClient
from authentications.apps import InvalidAccessToken
import logging
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import UPDATE_HOLD_STATUS
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
from web_admin.api_logger import API_Logger
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)
logging.captureWarnings(True)

class HoldVoucher(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(HoldVoucher, self).dispatch(request, *args, **kwargs)

    def post(self, request, voucher_id):
        success_count = 0
        failed_count = 0
        success_ids = []
        failed_ids = []
        ids = request.POST.getlist("ids[]")
        params = {
            'is_on_hold': True
        }
        for i in ids:
            self.logger.info('========== Start hold voucher ==========')
            url = settings.DOMAIN_NAMES + UPDATE_HOLD_STATUS.format(voucher_id=i)
            is_success, status_code, status_message, data = RestFulClient.put(url=url,
                                                                           loggers=self.logger, headers=self._get_headers(),
                                                                           params=params)
            if is_success:
                success_count  += 1
                success_ids.append(i)
            elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            else:
                failed_count += 1
                failed_ids.append(i)
            self.logger.info('========== Finish hold voucher ==========')

        return JsonResponse({"success_ids":success_ids, "success_count":success_count, "failed_count":failed_count})

class UnholdVoucher(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UnholdVoucher, self).dispatch(request, *args, **kwargs)

    def post(self, request, voucher_id):
        success_count = 0
        failed_count = 0
        success_ids = []
        failed_ids = []
        ids = request.POST.getlist("ids[]")
        params = {
            'is_on_hold': False
        }
        for i in ids:
            self.logger.info('========== Start unhold voucher ==========')
            url = settings.DOMAIN_NAMES + UPDATE_HOLD_STATUS.format(voucher_id=i)
            is_success, status_code, status_message, data = RestFulClient.put(url=url,
                                                                           loggers=self.logger, headers=self._get_headers(),
                                                                           params=params)
            if is_success:
                success_count  += 1
                success_ids.append(i)
            elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            else:
                failed_count += 1
                failed_ids.append(i)
            self.logger.info('========== Finish unhold voucher ==========')

        return JsonResponse({"success_ids":success_ids, "success_count":success_count, "failed_count":failed_count})
