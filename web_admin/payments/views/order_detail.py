from braces.views import GroupRequiredMixin
from web_admin import setup_logger
from django.shortcuts import render
from django.views.generic.base import TemplateView
import logging
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import PAYMENT_URL, PAYMENT_ORDER_DETAIL_URL
from django.contrib import messages
from authentications.utils import check_permissions_by_user, get_correlation_id_from_username
from web_admin.api_logger import API_Logger

logger = logging.getLogger(__name__)

STATUS_ORDER = {
    -1: 'Fail',
     0: 'Created',
     1: 'Locking',
     2: 'Executed',
     3: 'Rolled back',
     4: 'Time out',
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
        page_from = request.session.get('page_from')
        agent_id = request.session.get('agent_id',None)
        customer_id = request.session.get('customer_id',None)
        request.session['redirect_from_detail'] = True
        back_wallet_url =request.session.get('back_wallet_url',None)
        data = self.get_payment_order_list(orderId=order_id)
        order_balance_movement = []
        additional_references = []
        total_credit = 0
        total_debit = 0
        if data :
            data['status'] = STATUS_ORDER.get(data['status'], 'UN_KNOWN')
            data['is_deleted'] = IS_DELETED.get(data.get('is_deleted'))
            data['initiator_user']['sof_type_id'] = SOF_TYPE.get(data['initiator_user']['sof_type_id'])
            data['payer_user']['sof_type_id'] = SOF_TYPE.get(data['payer_user']['sof_type_id'])
            data['payee_user']['sof_type_id'] = SOF_TYPE.get(data['payee_user']['sof_type_id'])
            order_balance_movement = data['order_balance_movements']
            additional_references = data['additional_references']
            for order in order_balance_movement:
                order['converted_status'] = BALANCE_MOVEMENT_STATUS_ORDER.get(order['status'], 'UN_KNOWN')
                if order['action_type'].lower() == "debit":
                    total_debit += order['amount']
                    order['debit_amount'] = order['amount']
                    order['credit_amount'] = '-'
                if order['action_type'].lower() == "credit":
                    total_credit += order['amount']
                    order['credit_amount'] = order['amount']
                    order['debit_amount'] = '-'
        context['data'] = data
        context['order_balance_movement'] = order_balance_movement
        context['additional_references'] = additional_references
        context['total_credit'] = total_credit
        context['total_debit'] = total_debit
        context['page_from'] = page_from
        context['agent_id'] = agent_id
        context['customer_id'] = customer_id
        context['back_wallet_url'] = back_wallet_url
        self.logger.info('========== End getting order detail ==========')
        return render(request, self.template_name, context)

    def get_payment_order_list(self, orderId):
        url = PAYMENT_ORDER_DETAIL_URL.format(order_id=orderId)

        is_success, status_code, data = RestFulClient.get(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger)

        API_Logger.post_logging(loggers=self.logger, response=data,
                                status_code=status_code, is_getting_list=False)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                "Something went wrong"
            )
            data = []
        return data