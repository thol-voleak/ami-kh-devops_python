from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from web_admin.api_settings import SERVICE_LIST_URL
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "services/services_list.html"

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = self.get_services_list()
        result = {'data': data}
        return result

    def get_services_list(self):
        url = SERVICE_LIST_URL
        data, success = self._get_method(api_path=url, func_description="service list", is_getting_list=True)
        return data
