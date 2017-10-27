from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import CASH_SOFS_URL

from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin

from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.api_logger import API_Logger
from web_admin.restful_client import RestFulClient
import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CashSOFView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_SEARCH_CASH_SOF_CREATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "cash_sof.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CashSOFView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search cash source of fund ==========')

        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type_id')
        currency = request.POST.get('currency')
        opening_page_index = request.POST.get('current_page_index')

        self.logger.info('user_id: {}'.format(user_id))
        self.logger.info('user_type_id: {}'.format(user_type_id))
        self.logger.info('currency: {}'.format(currency))

        body = {}
        if user_id is not '':
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not '0':
            body['user_type'] = int(0 if user_type_id is None else user_type_id)
        if currency is not '':
            body['currency'] = currency

        data = self.get_cash_sof_list(body,opening_page_index)
                
        if data is not None:
            data = self.format_data(data)
        result_data = data.get('cash_sofs', [])
        page = data.get("page", {})

        context = {'sof_list': result_data,
                   'user_id': user_id,
                   'user_type_id': user_type_id,
                   'currency': currency,
                   'search_count': page.get('total_elements', 0),
                   'paginator': page,
                   'page_range': calculate_page_range_from_page_info(page)
                    }
        self.logger.info('========== End search cash source of fund ==========')
        return render(request, self.template_name, context)

    def get_cash_sof_list(self, body,opening_page_index):
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        success, status_code, status_message, data = RestFulClient.post(url=CASH_SOFS_URL, headers=self._get_headers(),
                                                                        params=body, loggers=self.logger)
        data = data or {}
        API_Logger.post_logging(
            loggers=self.logger,
            params=body,
            response=data.get('cash_sofs', []),
            status_code=status_code,
            is_getting_list=True
        )
        return data

    def format_data(self, data):
        for i in data['cash_sofs']:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
