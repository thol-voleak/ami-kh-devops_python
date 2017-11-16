from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info

import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class HistoryView(GetHeaderMixin, GroupRequiredMixin, TemplateView):
    group_required = "CAN_SEARCH_CARD_HISTORY"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "history.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(HistoryView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search history card ==========')

        trans_id = request.GET.get('trans_id')
        card_id = request.GET.get('card_id')
        user_id = request.GET.get('user_id')
        user_type_id = request.GET.get('user_type_id')

        if (trans_id, card_id, user_id, user_type_id) == (None, None, None, None):
            result_data = {}
            page = {'total_pages': 1, 'current_page': 1}
        else:
            body = {'paging': True, 'page_index': int(request.GET.get('current_page_index'))}
            if trans_id is not '':
                body['trans_id'] = trans_id
            if card_id is not '':
                body['card_id'] = int(0 if card_id is None else card_id)
            if user_id is not '':
                body['user_id'] = int(0 if user_id is None else user_id)
            if user_type_id is not '' and user_type_id is not '0':
                body['user_type_id'] = int(0 if user_type_id is None else user_type_id)

            data = self.get_card_history_list(body)
            page = data.get("page", {})
            self.logger.info('Page: {}'.format(page))
            data = data.get('card_histories', [])
            if data is not None:
                result_data = self.format_data(data)
            else:
                result_data = data

        context = {'data': result_data,
                   'paginator': page,
                   'page_range': calculate_page_range_from_page_info(page),
                   'trans_id': "" if trans_id is None else trans_id,
                   'card_id': str("" if card_id is None else card_id),
                   'user_id': str("" if user_id is None else user_id),
                   'user_type_id': user_type_id
                   }

        self.logger.info('========== End search card history ==========')
        return render(request, 'history.html', context)

    def get_card_history_list(self, body):
        url = api_settings.CARD_HISTORY_PATH
        success, status_code, status_message, data = RestFulClient.post(url=url, headers=self._get_headers(), params=body, loggers=self.logger)
        data = data or {}
        API_Logger.post_logging(
            loggers=self.logger,
            params=body,
            response=data.get('card_histories', []),
            status_code = status_code,
            is_getting_list = True
        )
        if isinstance(data, dict):
            return data
        else:
            return {}

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
