from web_admin.api_settings import SERVICE_LIST_URL
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "services/services_list.html"

    def get_context_data(self, **kwargs):
        data = self.get_services_list()
        result = {'data': data}
        return result

    def get_services_list(self):
        url = SERVICE_LIST_URL
        data, success = self._get_method(url, "service list", logger, True)
        return data
