from braces.views import GroupRequiredMixin
from web_admin import setup_logger
from django.shortcuts import render
from django.views.generic.base import TemplateView
import logging
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import PAYMENT_URL
from django.contrib import messages
from authentications.utils import check_permissions_by_user, get_correlation_id_from_username
from web_admin.api_logger import API_Logger

logger = logging.getLogger(__name__)

STATUS_ORDER = {
    -1: 'FAIL',
     0: 'CREATED',
     1: 'LOCKING',
     2: 'EXECUTED',
     3: 'ROLLED_BACK',
     4: 'TIME_OUT',
}

BALANCE_MOVEMENT_STATUS_ORDER = {
    -1: 'FAIL',
     0: 'CREATED',
     1: 'LOCKING',
     2: 'EXECUTED',
     3: 'TIME_OUT',
     4: 'ROLLED_BACK',
}

IS_DELETED = {
    True: 'Yes',
    False: 'No',
}

SOF_TYPE = {
    1: 'Bank',
    2: 'Cash',
    3: 'Card'
}

class OrderDetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "payments/order_detail.html"
    logger = logger

    group_required = "CAN_VIEW_PAYMENT_ORDER_DETAIL"
    login_url = 'web:permission_denied'
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(OrderDetailView, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting order detail ==========')
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        order_id = context['order_id']
        body = {
            'order_id': order_id
        }
        data = self.get_payment_order_list(body=body)
        order_balance_movement = []
        total_credit = 0
        total_debit = 0
        if data and data['orders']:
            data = data['orders'][0]
            data['status'] = STATUS_ORDER.get(data['status'], 'UN_KNOWN')
            data['is_deleted'] = IS_DELETED.get(data.get('is_deleted'))
            data['initiator']['sof_type_id'] = SOF_TYPE.get(data['initiator']['sof_type_id'])
            data['payer']['sof_type_id'] = SOF_TYPE.get(data['payer']['sof_type_id'])
            data['payee']['sof_type_id'] = SOF_TYPE.get(data['payee']['sof_type_id'])
            order_balance_movement = data['order_balance_movements']
            for order in order_balance_movement:
                order['converted_status'] = BALANCE_MOVEMENT_STATUS_ORDER.get(order['status'], 'UN_KNOWN')
                if order['action_type'] == "Debit":
                    total_debit += order['amount']
                    order['debit_amount'] = order['amount']
                    order['credit_amount'] = '-'
                if order['action_type'] == "Credit":
                    total_credit += order['amount']
                    order['credit_amount'] = order['amount']
                    order['debit_amount'] = '-'
        context['data'] = data
        context['order_balance_movement'] = order_balance_movement
        context['total_credit'] = total_credit
        context['total_debit'] = total_debit
        self.logger.info('========== End getting order detail ==========')
        return render(request, self.template_name, context)

    def get_payment_order_list(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=PAYMENT_URL,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data['orders'],
                                status_code=status_code, is_getting_list=False)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data