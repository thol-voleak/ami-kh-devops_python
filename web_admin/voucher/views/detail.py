from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from django.conf import settings
from braces.views import GroupRequiredMixin
from django.contrib import messages
from web_admin.api_settings import GET_VOUCHER_DETAIL

logger = logging.getLogger(__name__)


class VoucherDetail(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "voucher/detail.html"
    group_required = "CAN_VIEW_VOUCHER_DETAILS"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(VoucherDetail, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start get Vouchers details ==========')
        context = super(VoucherDetail, self).get_context_data(**kwargs)
        voucher_id = context['voucher_id']
        data = self.get_voucher_detail(voucher_id)
        self.logger.info('========== Fisnish get Vouchers details ==========')
        context.update({
            'data': data[0]
        })
        request.session['ref_page_url'] = request.build_absolute_uri()

        return render(request, self.template_name, context)

    def get_voucher_detail(self, voucher_id):
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
        return data['vouchers']