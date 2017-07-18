from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import GET_ALL_CURRENCY_URL

from authentications.utils import get_correlation_id_from_username
from django.conf import settings
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class CreateView(TemplateView, RESTfulMethods):
    template_name = "bank/create.html"
    url = settings.DOMAIN_NAMES + "api-gateway/sof-bank/v1/banks"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start create bank sofs ==========')
        currencies = self._get_currencies_list()
        context = {'currencies': currencies}
        self.logger.info('========== Finished create bank sofs ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating bank profile ==========')

        name = request.POST.get('name')
        bank_bin = request.POST.get('bin')
        is_active = request.POST.get('is_active', 1)
        description = request.POST.get('description')
        credit_url = request.POST.get('credit_url')
        debit_url = request.POST.get('debit_url')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        currency = request.POST.get('currency')
        check_status_url = request.POST.get('check_status_url')
        cancel_url = request.POST.get('cancel_url')
        connection_timeout = request.POST.get('connection_timeout')
        read_timeout = request.POST.get('read_timeout')

        if is_active == '1':
            is_active = bool(True)
        else:
            is_active = bool(False)

        params = {
            "name": name,
            "bin": bank_bin,
            "description": description,
            "is_active": is_active,
            "debit_url": debit_url,
            "credit_url": credit_url,
            "bank_account_number": account_number,
            "bank_account_name": account_name,
            "currency": currency,
            "check_status_url": check_status_url,
            "cancel_url": cancel_url,
            "connection_timeout": connection_timeout,
            "read_timeout": read_timeout
        }

        data, success = self._post_method(api_path=self.url,
                                          func_description="Bank Profile",
                                          logger=logger, params=params)
        if success:
            self.logger.info('========== Finished creating bank profile ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Add bank successfully'
            )
            return redirect('bank_sofs:bank_sofs_list')

    def _get_currencies_list(self):
        url = GET_ALL_CURRENCY_URL
        data, success = self._get_method(api_path=url,
                                         func_description="currency list from backend",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            value = data.get('value', '')
            currencies = [i.split('|') for i in value.split(',')]
        else:
            currencies = []
        return currencies
