from web_admin.restful_methods import RESTfulMethods

from django.conf import settings
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, RESTfulMethods):
    template_name = "bank/delete.html"
    get_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/report/v1/banks/{id}"
    delete_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/sof-bank/v1/banks/{id}"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get bank detail ==========')
        context = super(DeleteView, self).get_context_data(**kwargs)
        bank_id = context['bank_id']
        logger.info("Get bank detail with [{}] bank Id".format(bank_id))
        bank = self._get_bank_details(bank_id)
        context = {'bank': bank}
        logger.info('========== Finished get bank detail ==========')
        return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start delete bank source of fund ==========')
        bank_id = kwargs['bank_id']
        data, success = self._delete_method(api_path=self.delete_bank_sof_detail_url.format(id=bank_id),
                                            func_description="Delete bank source of fund",
                                            logger=logger)
        if success:
            logger.info('========== Finished delete bank source of fund ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Deleted bank account successfully'
            )
            return redirect('bank_sofs:bank_sofs_list')

    def _get_bank_details(self, bank_id):
        data, success = self._get_method(api_path=self.get_bank_sof_detail_url.format(id=bank_id),
                                         func_description="bank detail from backend",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            return data
