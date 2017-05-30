from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

import logging

logger = logging.getLogger(__name__)


class BankSofsListView(TemplateView, RESTfulMethods):
    template_name = "bank_sofs/list.html"
    url = "report/v1/banks"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get bank list ==========')
        # data, success = self._get_method(self.url, "get bank list", logger, True)
        logger.info('========== Finished get get bank list ==========')
        result = {'data': [{'name': 'klang'}]}
        return result
