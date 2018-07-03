from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger, api_settings
from web_admin.global_constants import REFUND_STATUS
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from django.contrib import messages
from web_admin.utils import calculate_page_range_from_page_info


logger = logging.getLogger(__name__)


class VoucherAdjustmentList(TemplateView, GetHeaderMixin):

    template_name = "voucher_adjustment/list.html"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(VoucherAdjustmentList, self).dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start render Vouchers Adjustment page==========')

        context = {
            'request_status_list': self._get_status_list(),
            'request_action_list': self._get_requested_action_list()
        }
        self.logger.info('========== Finish render Vouchers Adjustment page==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        request_id = request.POST.get('request_id')
        requested_by = request.POST.get('requested_by')
        request_action = request.POST.get('request_action')
        request_status = request.POST.get('request_status')
        original_voucher_id = request.POST.get('original_voucher_id')
        from_date = request.POST.get('requested_date_from')
        to_date = request.POST.get('requested_date_to')
        opening_page_index = request.POST.get('current_page_index')
        
        body = {}
        body['page_index'] = int(opening_page_index)
        if request_id != '':
            body['id'] = request_id
        if requested_by:
            body['requested_username'] = requested_by
        if request_status:
            body['status_id'] = int(request_status)
        if original_voucher_id:
            body['original_voucher_id'] = original_voucher_id

        if from_date:
            new_from_created_timestamp = datetime.strptime(from_date, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp

        if to_date:
            new_to_created_timestamp = datetime.strptime(to_date, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp

        self.logger.info('========== Start searching Voucher Adjustment ==========')
        data = self._search_for_vouchers(body)
        self.logger.info('========== Finished searching Voucher Adjustment ==========')

        page = data['page']
        context = {
            'data': self._format_data(data['refund_vouchers']),
            'paginator': page,
			'search_count': page['total_elements'],
			'page_range': calculate_page_range_from_page_info(page),
            'request_status_list': self._get_status_list(),
            'request_action_list': self._get_requested_action_list(),
            'request_id': request_id,
            'requested_by': requested_by,
            'selected_action': request_action,
            'selected_status': request_status,
            'original_voucher_id': original_voucher_id,
            'requested_date_from': from_date,
            'requested_date_to': to_date
        }
        return render(request, self.template_name, context)


    def _get_status_list(self):
        return REFUND_STATUS.items()
    
    def _get_requested_action_list(self):
        return [
            {"name": "REFUND", "value": "REFUND"},
        ]
    
    def _format_data(self, data):
        for i in data:
            i['status'] = REFUND_STATUS.get(str(i.get('status_id')))
            if i['status'] is None:
                i['status'] = 'Unknown({})'.format(i.get('status_id'))
        return data
    
    def _search_for_vouchers(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.SEARCH_VOUCHER_ADJUSTMENT,
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