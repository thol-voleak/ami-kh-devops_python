from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from web_admin.api_settings import CARD_SOFS_URL
from datetime import datetime
from django.views.generic.base import TemplateView
from django.shortcuts import render
from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info, make_download_file, export_file
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin

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
        opening_page_index = request.POST.get('current_page_index')

        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        if user_id is not '' and user_id is not None:
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not '0' and user_type_id is not None:
            body['user_type_id'] = int(0 if user_type_id is None else user_type_id)
        if currency is not '' and currency is not None:
            body['currency'] = currency

        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp

        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp

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

        return data, success, status_message
