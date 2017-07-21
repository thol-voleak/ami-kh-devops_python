from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "bank/list.html"
    url = "api-gateway/report/"+api_settings.API_VERSION+"/banks"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get bank list ==========')
        data, success = self._post_method(self.url, "get bank list", logger)

        if success:
            self.logger.info('========== Finished get get bank list ==========')
            result = {'data': data}
            return result
