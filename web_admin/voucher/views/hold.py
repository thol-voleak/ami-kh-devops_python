from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
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
        self.logger.info('========== Start hold voucher ==========')
        url = settings.DOMAIN_NAMES + UPDATE_HOLD_STATUS.format(voucher_id=voucher_id)
        params = {
            'is_on_hold': True
        }
        result = ajax_functions._put_method(request, url, "", self.logger, params)
        self.logger.info('========== Finish hold voucher ==========')
        return result

class UnholdVoucher(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UnholdVoucher, self).dispatch(request, *args, **kwargs)

    def post(self, request, voucher_id):
        self.logger.info('========== Start unhold voucher ==========')
        print("fsadsdbdfghdfghdfghdgh")
        url = settings.DOMAIN_NAMES + UPDATE_HOLD_STATUS.format(voucher_id=voucher_id)
        params = {
            'is_on_hold': False
        }
        result = ajax_functions._put_method(request, url, "", self.logger, params)
        self.logger.info('========== Finish unhold voucher ==========')
        return result

