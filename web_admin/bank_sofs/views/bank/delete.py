from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods

from django.conf import settings
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, RESTfulMethods):
    template_name = "bank/delete.html"
    get_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/report/v1/banks"
    delete_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/sof-bank/v1/banks/{id}"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get bank detail ==========')
        context = super(DeleteView, self).get_context_data(**kwargs)
        bank_id = context['bank_id']
        self.logger.info("Get bank detail with [{}] bank Id".format(bank_id))
        bank = self._get_bank_details(bank_id)
        context = {'bank': bank}
        self.logger.info('========== Finished get bank detail ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start delete bank source of fund ==========')
        bank_id = kwargs['bank_id']
        data, success = self._delete_method(api_path=self.delete_bank_sof_detail_url.format(id=bank_id),
                                            func_description="Delete bank source of fund",
                                            logger=logger)
        if success:
            self.logger.info('========== Finished delete bank source of fund ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Deleted bank account successfully'
            )
            return redirect('bank_sofs:bank_sofs_list')

    def _get_bank_details(self, bank_id):
        params = {
            'id': bank_id
        }
        data, success = self._post_method(self.get_bank_sof_detail_url,
                                          "bank detail from backend",
                                          logger,
                                          params=params)
        if success:
            return data[0]
