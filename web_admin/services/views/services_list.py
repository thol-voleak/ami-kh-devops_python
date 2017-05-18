from django.views.generic.base import TemplateView
from django.conf import settings
import logging
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class ListView(TemplateView, RESTfulMethods):
    template_name = "services/services_list.html"

    def get_context_data(self, **kwargs):
        data = self.get_services_list()
        result = {'data': data}
        return result

    def get_services_list(self):
        url = settings.SERVICE_LIST_URL
        data, sucess = self._get_method(url, "service list", logger, True)
        return data

