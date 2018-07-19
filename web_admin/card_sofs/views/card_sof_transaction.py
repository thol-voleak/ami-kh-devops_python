from web_admin.restful_methods import RESTfulMethods
from web_admin.api_logger import API_Logger
from datetime import datetime
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.utils import calculate_page_range_from_page_info
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
        provider_name = request.POST.get('provider_name')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        opening_page_index = request.POST.get('current_page_index')

        body = self.createSearchBody(from_created_timestamp, order_id, short_order_id, order_detail_id, sof_id, status,
                                     to_created_timestamp, action_id, user_id, user_type_id, provider_name)
        body['paging'] = True
        body['page_index'] = int(opening_page_index)

        context = {}
        data, success, status_message = self._get_card_sof_transaction(body=body)
        body['from_created_timestamp'] = from_created_timestamp
        body['to_created_timestamp'] = to_created_timestamp

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
            'from_created_timestamp': from_created_timestamp,
            'to_created_timestamp': to_created_timestamp
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

    def createSearchBody(self, from_created_timestamp, order_id, short_order_id, order_detail_id,
                         sof_id, status, to_created_timestamp, action_id, user_id, user_type_id, provider_name):
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
        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp
        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp
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
