import logging

from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.api_settings import PAYMENT_URL
from web_admin.restful_methods import RESTfulMethods
from django.template.loader import render_to_string
from django.http import JsonResponse

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class PaymentOrderView(TemplateView, RESTfulMethods):
    template_name = "payments/payment_order.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start searching payment order ==========')

        order_id = request.POST.get('order_id')
        service_name = request.POST.get('service_name')
        payer_user_id = request.POST.get('payer_user_id')
        payer_user_type_id = request.POST.get('payer_user_type_id')
        payee_user_id = request.POST.get('payee_user_id')
        payee_user_type_id = request.POST.get('payee_user_type_id')

        logger.info('order_id: {}'.format(order_id))
        logger.info('service_name: {}'.format(service_name))
        logger.info('payer_user_id: {}'.format(payer_user_id))
        logger.info('payer_user_type_id: {}'.format(payer_user_type_id))
        logger.info('payee_user_id: {}'.format(payee_user_id))
        logger.info('payee_user_type_id: {}'.format(payee_user_type_id))

        body = {}
        if order_id is not '':
            body['order_id'] = order_id
        if service_name is not '':
            body['service_name'] = service_name
        if payer_user_id is not '':
            body['payer_user_id'] = payer_user_id
        if payer_user_type_id is not '' and payer_user_type_id is not '0':
            body['payer_user_type_id'] = int(payer_user_type_id)
        if payee_user_id is not '':
            body['payee_user_id'] = payee_user_id
        if payee_user_type_id is not '' and payee_user_type_id is not '0':
            body['payee_user_type_id'] = int(payee_user_type_id)

        data, status = self.get_payment_order_list(body)
        if data is not None:
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
        list_content = render_to_string("payments/payment_order_table_content.html", context)
        logger.info('========== Finished searching payment order ==========')
        return JsonResponse({"status": status, "table_content": list_content})

    def get_payment_order_list(self, body):
        response, status = self._post_method(PAYMENT_URL, 'Payment Order List', logger, body)
        return response, status

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_SUCCESS.get(i.get('is_stopped'))
        return data
