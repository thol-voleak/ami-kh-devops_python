from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import PAYMENT_URL
from web_admin.restful_methods import RESTfulMethods

from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class PaymentOrderView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "payments/payment_order.html"
    logger = logger

    group_required = "CAN_SEARCH_PAYMENT_ORDER"
    login_url = 'authentications:login'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PaymentOrderView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start searching payment order ==========')

        order_id = request.POST.get('order_id')
        service_name = request.POST.get('service_name')
        payer_user_id = request.POST.get('payer_user_id')
        payer_user_type_id = request.POST.get('payer_user_type_id')
        payee_user_id = request.POST.get('payee_user_id')
        payee_user_type_id = request.POST.get('payee_user_type_id')

        self.logger.info('order_id: {}'.format(order_id))
        self.logger.info('service_name: {}'.format(service_name))
        self.logger.info('payer_user_id: {}'.format(payer_user_id))
        self.logger.info('payer_user_type_id: {}'.format(payer_user_type_id))
        self.logger.info('payee_user_id: {}'.format(payee_user_id))
        self.logger.info('payee_user_type_id: {}'.format(payee_user_type_id))

        body = {}
        if order_id:
            body['order_id'] = order_id
        if service_name:
            body['service_name'] = service_name
        if payer_user_id:
            body['payer_user_id'] = payer_user_id
        if payer_user_type_id.isdigit() and payer_user_type_id != '0':
            body['payer_user_type_id'] = int(payer_user_type_id)
        if payee_user_id:
            body['payee_user_id'] = payee_user_id
        if payee_user_type_id.isdigit() and payee_user_type_id != '0':
            body['payee_user_type_id'] = int(payee_user_type_id)

        data, status = self.get_payment_order_list(body)
        if data:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'order_list': result_data,
                   'order_id': order_id,
                   'service_name': service_name,
                   'payer_user_id': payer_user_id,
                   'payer_user_type_id':payer_user_type_id,
                   'payee_user_id': payee_user_id,
                   'payee_user_type_id':payee_user_type_id}
        self.logger.info('========== Finished searching payment order ==========')

        return render(request, self.template_name, context)

    def get_payment_order_list(self, body):
        response, status = self._post_method(PAYMENT_URL, 'Payment Order List', logger, body)
        return response, status

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_SUCCESS.get(i.get('is_stopped'))
        return data
