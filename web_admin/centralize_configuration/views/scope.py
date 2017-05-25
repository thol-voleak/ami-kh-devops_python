from django.views.generic.base import TemplateView
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods

import logging

logger = logging.getLogger(__name__)


class ScopeListView(TemplateView, RESTfulMethods):
    template_name = 'centralize_configuration/scope_list.html'

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting all configuration scope ==========')
            url =  api_settings.SCOPES_URL
            data, success = self._get_method(url, 'configuration scope', logger)
            if success:
                data = {'scopes': data}
                logger.info(
                    '========== Finish getting all configuration scope ==========')
                return data
        except Exception as e:
            raise Exception(e)
