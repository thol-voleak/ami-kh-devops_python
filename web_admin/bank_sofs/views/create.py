from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class BankSofsCreateView(TemplateView, RESTfulMethods):
    template_name = "bank_sofs/create.html"
    url = "report/v1/banks"

    def get_context_data(self, **kwargs):
        logger.info('========== Start create bank sofs ==========')
        context = super(BankSofsCreateView, self).get_context_data(**kwargs)
        logger.info('========== Finished create bank sofs ==========')
        return context
