from web_admin.restful_methods import RESTfulMethods

from django.conf import settings
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class DetailsView(TemplateView, RESTfulMethods):
    template_name = "bank_sof/detail.html"
    get_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/report/v1/banks/{id}"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get bank detail ==========')
        context = super(DetailsView, self).get_context_data(**kwargs)
        bank_id = context['bank_id']
        logger.info("Get bank detail with [{}] bank Id".format(bank_id))
        bank = self._get_bank_details(bank_id)
        context = {'bank': bank}
        logger.info('========== Finished get bank detail ==========')
        return context

    def _get_bank_details(self, bank_id):
        data, success = self._get_method(api_path=self.get_bank_sof_detail_url.format(id=bank_id),
                                         func_description="bank detail from backend",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            return data