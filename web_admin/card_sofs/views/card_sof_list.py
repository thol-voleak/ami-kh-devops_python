from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from datetime import date, timedelta
from web_admin.api_logger import API_Logger
from web_admin.api_settings import CARD_SOFS_URL
from django.views.generic.base import TemplateView
from django.shortcuts import render
from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info, make_download_file, export_file, convert_string_to_date_time
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages

import logging

logger = logging.getLogger(__name__)


class CardSOFView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_SEARCH_CARD_SOF_CREATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "sof/card_sof.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardSOFView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {"search_count": 0}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start {} card SOF =========='.format('download' if 'download' in request.POST else 'search'))

        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type_id')
        currency = request.POST.get('currency')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        from_created_time = request.POST.get('from_created_time')
        to_created_time = request.POST.get('to_created_time')
        opening_page_index = request.POST.get('current_page_index')

        body = {'paging': True, 'page_index': int(opening_page_index)}
        if user_id is not '' and user_id is not None:
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not '0' and user_type_id is not None:
            body['user_type_id'] = int(0 if user_type_id is None else user_type_id)
        if currency is not '' and currency is not None:
            body['currency'] = currency

        if from_created_timestamp:
            body['from_created_timestamp'] = convert_string_to_date_time(from_created_timestamp, from_created_time)
        if to_created_timestamp:
            body['to_created_timestamp'] = convert_string_to_date_time(to_created_timestamp, to_created_time)

        context = {}
        if 'download' in request.POST:
            file_type = request.POST.get('export-type')
            body['file_type'] = file_type
            body['row_number'] = 5000
            is_success, data = export_file(self, body=body, url_download=CARD_SOFS_URL, api_logger=API_Logger)
            if is_success:
                response = make_download_file(data, file_type)
                self.logger.info('========== End export card source of fund ==========')
                return response
        else:
            data, success, status_message = self._get_card_sof_list(body=body)
            body['from_created_timestamp'] = from_created_timestamp
            body['to_created_timestamp'] = to_created_timestamp

            if success:
                cards_list = data.get("card_sofs", [])
                page = data.get("page", {})
                self.logger.info("Page: {}".format(page))
                context.update({
                    'search_by.user_id':  user_id,
                    'search_by.currency': currency,
                    'search_by.user_type_id': user_type_id,
                    'search_by.from_created_timestamp': from_created_timestamp,
                    'from_created_time': from_created_time,
                    'search_by.to_created_timestamp': to_created_timestamp,
                    'to_created_time': to_created_time,
                    'search_count': page.get('total_elements', 0),
                    'paginator': page,
                    'page_range': calculate_page_range_from_page_info(page),
                    'card_sof_list': cards_list,
                    'search_by': body,
                    'is_show_export': check_permissions_by_user(self.request.user,"CAN_EXPORT_CARD_SOF_INFORMATION")
                })
            else:
                context.update({
                    'search_count': 0,
                    'paginator': {},
                    'card_sof_list': [],
                    'search_by': body,
                    'is_show_export': False
                })
            self.logger.info('========== End search card SOF ==========')
            return render(request, self.template_name, context)


    def _get_card_sof_list(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=CARD_SOFS_URL,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)
        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('card_sofs', []),
                                status_code=status_code, is_getting_list=True)

        if not success:
            if status_code == "Timeout":
                self.logger.error('Search service group list request timeout')
                status_message = 'Search timeout, please try again or contact technical support'
            else:
                self.logger.error('Search service group list request failed')
                status_message = 'Search failed, please try again or contact support'

            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )

        return data, success, status_message
