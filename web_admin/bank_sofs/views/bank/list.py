from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "bank/list.html"
    url = "api-gateway/report/v1/banks"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get bank list ==========')
        data, success = self._post_method(self.url, "get bank list", logger)
        
        if success:
            self.logger.info('========== Finished get get bank list ==========')
            result = {'data': data}
            return result
