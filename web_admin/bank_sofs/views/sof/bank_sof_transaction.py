from web_admin.restful_methods import RESTfulMethods
from web_admin.api_logger import API_Logger
from datetime import date, timedelta
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info, convert_string_to_date_time
from web_admin import api_settings, setup_logger, RestFulClient
import logging

logger = logging.getLogger(__name__)


class BankSOFTransaction(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_SEARCH_BANK_TXN"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "sof/bank_transaction.html"
    search_bank_transaction = settings.DOMAIN_NAMES + "api-gateway/report/" + api_settings.API_VERSION + "/banks/transactions"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BankSOFTransaction, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {"search_count": 0}
        self.initSearchDateTime(context)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start searching bank SOF transaction  ==========')

        sof_id = request.POST.get('sof_id')
        order_id = request.POST.get('order_id')
        short_order_id = request.POST.get('short_order_id')
        status = request.POST.get('status')
        type = request.POST.get('type')
        created_from_date = request.POST.get('created_from_date')
        created_to_date = request.POST.get('created_to_date')
        created_from_time = request.POST.get('created_from_time')
        created_to_time = request.POST.get('created_to_time')
        opening_page_index = request.POST.get('current_page_index')
        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type_id')
        modified_from_date = request.POST.get('modified_from_date')
        modified_from_time = request.POST.get('modified_from_time')
        modified_to_date = request.POST.get('modified_to_date')
        modified_to_time = request.POST.get('modified_to_time')
        order_detail_id = request.POST.get('order_detail_id')
        bank_name = request.POST.get('bank_name')

        body = self.createSearchBody(created_from_date, order_id, short_order_id, sof_id, status,
                                     created_to_date, type, user_id, user_type_id, created_from_time,
                                     created_to_time, modified_from_date, modified_from_time, modified_to_date ,
                                     modified_to_time, order_detail_id, bank_name)
        body['paging'] = True
        body['page_index'] = int(opening_page_index)

        context = {}
        data, success, status_message = self._get_sof_bank_transaction(body=body)

        if success:
            cards_list = data.get("bank_sof_transactions", [])
            page = data.get("page", {})
            self.logger.info("Page: {}".format(page))
            context.update(
                {'search_count': page.get('total_elements', 0),
                 'paginator': page,
                 'page_range': calculate_page_range_from_page_info(page),
                 'user_id': user_id,
                 'transaction_list': cards_list,
                 'search_by': body,
                 'created_from_date': created_from_date,
                 'created_to_date': created_to_date,
                 'created_from_time': created_from_time,
                 'created_to_time': created_to_time,
                 'modified_from_date': modified_from_date,
                 'modified_from_time': modified_from_time,
                 'modified_to_date': modified_to_date,
                 'modified_to_time': modified_to_time,
                 'user_type_id': user_type_id,
                 'order_detail_id': order_detail_id,
                 'bank_name': bank_name
                 }
            )
        else:
            context.update(
                {'search_count': 0,
                 'paginator': {},
                 'user_id': user_id,
                 'transaction_list': [],
                 'search_by': body,
                 'created_from_date': created_from_date,
                 'created_to_date': created_to_date,
                 'created_from_time': created_from_time,
                 'created_to_time': created_to_time,
                 'modified_from_date': modified_from_date,
                 'modified_from_time': modified_from_time,
                 'modified_to_date': modified_to_date,
                 'modified_to_time': modified_to_time,
                 'user_type_id': user_type_id,
                 'order_detail_id': order_detail_id,
                 'bank_name': bank_name
                 }
            )

        self.logger.info('========== Start searching bank SOF transaction ==========')
        return render(request, self.template_name, context)

    def createSearchBody(self, created_from_date, order_id, short_order_id, sof_id, status, created_to_date,
                         type, user_id, user_type_id, created_from_time, created_to_time, modified_from_date,
                         modified_from_time, modified_to_date, modified_to_time, order_detail_id, bank_name):
        body = {}
        if sof_id is not '' and sof_id is not None:
            body['sof_id'] = int(sof_id)
        if order_id is not '' and order_id is not None:
            body['order_id'] = order_id
        if short_order_id is not '' and short_order_id is not None:
            body['short_order_id'] = short_order_id
        if status is not '' and status is not None:
            body['status_id'] = [int(status)]
        if type is not '' and type is not None:
            body['action_id'] = int(type)
        if created_from_date is not '' and created_from_date is not None:
            body['from_created_timestamp'] = convert_string_to_date_time(created_from_date, created_from_time)
        if created_to_date is not '' and created_to_date is not None:
            body['to_created_timestamp'] = convert_string_to_date_time(created_to_date, created_to_time)
        if modified_from_date is not '' and modified_from_date is not None:
            body['from_last_updated_timestamp'] = convert_string_to_date_time(modified_from_date, modified_from_time)
        if modified_to_date is not '' and modified_to_date is not None:
            body['to_last_updated_timestamp'] = convert_string_to_date_time(modified_to_date, modified_to_time)
        if user_id is not '' and user_id is not None:
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not None and user_type_id is not '0':
            body['user_type_id'] = int(user_type_id)
        if order_detail_id is not ''and order_detail_id is not None:
            body['order_detail_id'] = order_detail_id
        if bank_name is not ''and bank_name is not None:
            body['bank_name'] = bank_name
        return body

    def _get_sof_bank_transaction(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=self.search_bank_transaction,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body)
        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('bank_sof_transactions', []),
                                status_code=status_code, is_getting_list=True)
        return data, success, status_message

    def initSearchDateTime(self, context):
        today = date.today()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)
        context['created_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['created_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['created_from_time'] = "00:00:00"
        context['created_to_time'] = "00:00:00"
        context['modified_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['modified_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['modified_from_time'] = "00:00:00"
        context['modified_to_time'] = "00:00:00"