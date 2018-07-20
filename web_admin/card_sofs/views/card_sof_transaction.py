from web_admin.restful_methods import RESTfulMethods
from web_admin.api_logger import API_Logger
from datetime import date, timedelta
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.utils import calculate_page_range_from_page_info, convert_string_to_date_time
import logging

logger = logging.getLogger(__name__)


class CardSOFTransaction(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_SEARCH_CARD_TXN"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "sof/card_sof_transaction.html"
    search_card_transaction = settings.DOMAIN_NAMES + "api-gateway/report/" + api_settings.API_VERSION + "/cards/transactions"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardSOFTransaction, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {"search_count": 0}
        self.init_search_datetime(context)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search card sof transaction ==========')

        sof_id = request.POST.get('sof_id')
        order_id = request.POST.get('order_id')
        short_order_id = request.POST.get('short_order_id')
        order_detail_id = request.POST.get('order_detail_id')
        status = request.POST.get('status')
        action_id = request.POST.get('action_id')
        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type_id')
        card_design_name = request.POST.get('card_design_name')
        card_design_number = request.POST.get('card_design_number')
        provider_name = request.POST.get('provider_name')
        card_account_name = request.POST.get('card_account_name')
        card_account_number = request.POST.get('card_account_number')

        created_from_date = request.POST.get('created_from_date')
        created_to_date = request.POST.get('created_to_date')
        created_from_time = request.POST.get('created_from_time')
        created_to_time = request.POST.get('created_to_time')

        opening_page_index = request.POST.get('current_page_index')

        body = self.createSearchBody(order_id, short_order_id, order_detail_id, sof_id, status,
                                     action_id, user_id, user_type_id, provider_name,
                                     card_design_number, card_design_name, card_account_name, card_account_number,
                                     created_from_date, created_from_time, created_to_date, created_to_time)
        body['paging'] = True
        body['page_index'] = int(opening_page_index)

        context = {}
        data, success, status_message = self._get_card_sof_transaction(body=body)

        context.update({
            'sof_id': sof_id,
            'order_id': order_id,
            'short_order_id': short_order_id,
            'order_detail_id': order_detail_id,
            'status': status,
            'action_id': action_id,
            'user_id': user_id,
            'user_type_id': user_type_id,
            'provider_name': provider_name,
            'card_design_number': card_design_number,
            'card_design_name': card_design_name,
            'card_account_name': card_account_name,
            'card_account_number': card_account_number,
            'created_from_date': created_from_date,
            'created_to_date': created_to_date,
            'created_from_time': created_from_time,
            'created_to_time': created_to_time,
        })

        if success:
            cards_list = data.get("card_sof_transactions", [])
            page = data.get("page", {})
            self.logger.info("Page: {}".format(page))
            context.update({
                'search_count': page.get('total_elements', 0),
                'paginator': page,
                'page_range': calculate_page_range_from_page_info(page),
                'transaction_list': cards_list
            })
        else:
            context.update({
                'search_count': 0,
                'paginator': {},
                'transaction_list': [],
            })
        self.logger.info('========== End search card sof transaction ==========')
        return render(request, self.template_name, context)

    def createSearchBody(self, order_id, short_order_id, order_detail_id,
                         sof_id, status, action_id, user_id, user_type_id, provider_name,
                         card_design_number, card_design_name, card_account_name, card_account_number,
                         created_from_date, created_from_time, created_to_date, created_to_time):
        body = {}
        if sof_id is not '' and sof_id is not None:
            body['sof_id'] = int(sof_id)
        if order_id is not '' and order_id is not None:
            body['order_id'] = order_id
        if short_order_id is not '' and short_order_id is not None:
            body['short_order_id'] = short_order_id
        if order_detail_id is not '' and order_detail_id is not None:
            body['order_detail_id'] = order_detail_id
        if status is not '' and status is not None:
            body['status_id'] = [int(status)]
        if action_id is not '' and action_id is not None and action_id is not '0':
            body['action_id'] = int(action_id)
        if user_id is not '' and user_id is not None:
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not None and user_type_id is not '0':
            body['user_type_id'] = int(user_type_id)
        if provider_name is not '' and provider_name is not None:
            body['provider_name'] = provider_name
        if card_design_number is not '' and card_design_number is not None:
            body['card_design_number'] = card_design_number
        if card_design_name is not '' and card_design_name is not None:
            body['card_design_name'] = card_design_name
        if card_account_name is not '' and card_account_name is not None:
            body['card_account_name'] = card_account_name
        if card_account_number is not '' and card_account_number is not None:
            body['card_account_number'] = card_account_number
        if created_from_date:
            body['from_created_timestamp'] = convert_string_to_date_time(created_from_date, created_from_time)
        if created_to_date:
            body['to_created_timestamp'] = convert_string_to_date_time(created_to_date, created_to_time)
        return body

    def _get_card_sof_transaction(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=self.search_card_transaction,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body)
        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('card_sof_transactions', []),
                                status_code=status_code, is_getting_list=True)

        return data, success, status_message

    @staticmethod
    def init_search_datetime(context):
        today = date.today()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)
        context['created_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['created_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['created_from_time'] = "00:00:00"
        context['created_to_time'] = "00:00:00"
