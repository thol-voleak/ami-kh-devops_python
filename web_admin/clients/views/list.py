from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
import logging
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username


logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "clients/clients_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info("========== Start Getting client list ==========")
        data = self.get_clients_list()
        result = {'data': data,
                  'msg': self.request.session.pop('client_update_msg', None),
                  'add_client_msg': self.request.session.pop('add_client_msg', None)}
        self.logger.info("========== Finish Getting client list ==========")
        return result

    def get_clients_list(self):
        url = api_settings.CLIENTS_LIST_URL
        data, success = self._get_method(url, 'Client List', logger, True)
        return data
