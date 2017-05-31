from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render

import logging

logger = logging.getLogger(__name__)


class BankSofsCreateView(TemplateView, RESTfulMethods):
    template_name = "bank_sofs/create.html"
    url = "api-gateway/sof-bank/v1/banks"

    def get_context_data(self, **kwargs):
        logger.info('========== Start create bank sofs ==========')
        context = super(BankSofsCreateView, self).get_context_data(**kwargs)
        logger.info('========== Finished create bank sofs ==========')
        return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start creating bank profile ==========')
        name = request.POST.get('name')
        bank_bin = request.POST.get('bin')
        is_active = request.POST.get('is_active')
        description = request.POST.get('description')
        credit_url = request.POST.get('credit_url')
        debit_url = request.POST.get('debit_url')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        currency = request.POST.get('currency')

        params = {
            "name": name,
            "bin": bank_bin,
            "description": description,
            "is_active": is_active,
            "debit_url": debit_url,
            "credit_url": credit_url,
            "account_number": account_number,
            "account_name": account_name,
            "currency": currency
        }

        data, success = self._post_method(api_path=self.url,
                                          func_description="Bank Profile",
                                          logger=logger, params=params)

        logger.info('========== Finished creating bank profile ==========')
        return render(request, 'bank_sofs/list.html')
