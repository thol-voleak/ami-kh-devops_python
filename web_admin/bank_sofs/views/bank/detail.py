from web_admin.restful_methods import RESTfulMethods

from web_admin.utils import setup_logger
from django.conf import settings
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class DetailsView(TemplateView, RESTfulMethods):
    template_name = "bank/detail.html"
    get_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/report/v1/banks"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(DetailsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get bank detail ==========')
        context = super(DetailsView, self).get_context_data(**kwargs)
        bank_id = context['bank_id']
        self.logger.info("Get bank detail with [{}] bank Id".format(bank_id))
        bank = self._get_bank_details(bank_id)
        context = {'bank': bank}
        self.logger.info('========== Finished get bank detail ==========')
        return context

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
