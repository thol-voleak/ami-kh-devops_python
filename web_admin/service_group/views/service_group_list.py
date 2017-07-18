from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
import logging
from authentications.utils import get_correlation_id_from_username
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "service_group/service_group_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get Service Group List ==========')
        data = self.get_service_group_list()
        self.logger.info('========== Finished get Service Group List ==========')
        result = {'data': data}
        return result

    def get_service_group_list(self):
        url = api_settings.SERVICE_GROUP_LIST_URL
        data, success = self._get_method(url, "service group list", logger, True)
        return data


