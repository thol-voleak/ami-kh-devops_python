from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from braces.views import GroupRequiredMixin
from django.contrib import messages


logger = logging.getLogger(__name__)


class VoucherList(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "voucher/list.html"
    group_required = "CAN_VIEW_VOUCHER_LIST"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(VoucherList, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        status_list = self._get_status_list()
        context = {
            'claim_status_list': status_list,
            'hold_status_list': self._get_hold_status_list(),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        voucher_id = request.POST.get('voucher_id')
        claim_status = request.POST.get('claim_status')
        cash_in_id = request.POST.get('cash_in_id')
        cash_out_id = request.POST.get('cash_out_id')
        from_date = request.POST.get('create_date_from')
        to_date = request.POST.get('create_date_to')
        expire_from_date = request.POST.get('expiration_date_from')
        expire_to_date = request.POST.get('expiration_date_to')
        hold_status = request.POST.get('hold_status')

        body = {}
        if cash_in_id:
            body['cash_in_user_id'] = int(cash_in_id)
        if cash_out_id:
            body['cash_out_user_id'] = int(cash_out_id)
        if voucher_id:
            body['voucher_id'] = int(voucher_id)
        if claim_status == 'True':
            body['is_used'] = True
        if claim_status == 'False':
            body['is_used'] = False
        if hold_status != '':
            body['is_on_hold'] = True if hold_status == 'True' else False

        if from_date:
            new_from_created_timestamp = datetime.strptime(from_date, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp

        if to_date:
            new_to_created_timestamp = datetime.strptime(to_date, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp

        if expire_from_date:
            new_expire_from_timestamp = datetime.strptime(expire_from_date, "%Y-%m-%d")
            new_expire_from_timestamp = new_expire_from_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_expire_date_timestamp'] = new_expire_from_timestamp

        if expire_to_date:
            new_to_expire_timestamp = datetime.strptime(expire_to_date, "%Y-%m-%d")
            new_to_expire_timestamp = new_to_expire_timestamp.replace(hour=23, minute=59, second=59)
            new_to_expire_timestamp = new_to_expire_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_expire_date_timestamp'] = new_to_expire_timestamp

        self.logger.info('========== Start searching Vouchers ==========')
        data = self._search_for_vouchers(body)
        self.logger.info('========== Finished searching Vouchers ==========')
        permissions = {}
        permissions['CAN_VIEW_VOUCHER_DETAILS'] = check_permissions_by_user(self.request.user,
                                                                            'CAN_VIEW_VOUCHER_DETAILS')
        context = {
            'data': data,
            'voucher_id': voucher_id,
            'claim_status_list': self._get_status_list(),
            'selected_status': claim_status,
            'cash_in_id': cash_in_id,
            'cash_out_id': cash_out_id,
            'create_date_from': from_date,
            'create_date_to': to_date,
            'expiration_date_from': expire_from_date,
            'expiration_date_to': expire_to_date,
            'permissions': permissions,
            'hold_status_list': self._get_hold_status_list(),
            'hold_status': hold_status,
        }
        return render(request, self.template_name, context)


    def _get_status_list(self):
        return [
            {"name": "All", "value": ""},
            {"name": "Used", "value": "True"},
            {"name": "Unused", "value": "False"},
        ]

    def _get_hold_status_list(self):
        return [
            {"name": "All", "value": ""},
            {"name": "Hold", "value": "True"},
            {"name": "Unhold", "value": "False"},
        ]

    def _search_for_vouchers(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.SEARCH_VOUCHERS,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data