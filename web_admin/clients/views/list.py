from django.views.generic.base import TemplateView
from web_admin import api_settings
import logging
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class ListView(TemplateView, RESTfulMethods):
    template_name = "clients/clients_list.html"

    def get_context_data(self, **kwargs):
        logger.info("========== Start Getting client list ==========")
        data = self.get_clients_list()
        result = {'data': data,
                  'msg': self.request.session.pop('client_update_msg', None)}
        logger.info("========== Finish Getting client list ==========")
        return result

    def get_clients_list(self):
        url = api_settings.CLIENTS_LIST_URL
        data, success = self._get_method(url, 'Client List', logger, True)
        return data
