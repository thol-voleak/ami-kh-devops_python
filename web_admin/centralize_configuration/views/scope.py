from django.views.generic.base import TemplateView
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
import logging

logger = logging.getLogger(__name__)


class ScopeListView(TemplateView, RESTfulMethods):
    template_name = 'centralize_configuration/scope_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ScopeListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting all configuration scope ==========')
        url =  api_settings.SCOPES_URL
        data, success = self._get_method(url, 'configuration scope', logger)
        if success:
            data = {'scopes': data}
            self.logger.info('========== Finish getting all configuration scope ==========')
            return data

