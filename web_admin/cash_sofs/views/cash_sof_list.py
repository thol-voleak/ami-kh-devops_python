from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from web_admin.api_settings import CASH_SOFS_URL
from web_admin.restful_methods import RESTfulMethods

from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CashSOFView(TemplateView, RESTfulMethods):
    template_name = "cash_sof.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CashSOFView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search cash source of fund ==========')

        user_id = request.GET.get('user_id')
        user_type_id = request.GET.get('user_type_id')
        currency = request.GET.get('currency')

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

        data = self.get_cash_sof_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'sof_list': result_data,
                   'user_id': user_id,
                   'user_type_id': user_type_id,
                   'currency': currency
                   }
        self.logger.info('========== End search cash source of fund ==========')
        return render(request, self.template_name, context)

    def get_cash_sof_list(self, body):
        response, status = self._post_method(CASH_SOFS_URL, 'Cash Source of Fund List', logger, body)
        return response

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
