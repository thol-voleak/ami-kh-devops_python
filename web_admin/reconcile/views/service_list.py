import json
import logging

from django.http import HttpResponse
from django.views.generic.base import TemplateView

from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger

logger = logging.getLogger(__name__)

class ServiceList(TemplateView, RESTfulMethods):

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ServiceList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        service_group_id = request.GET.get('service_group_id')
        services_list = self._get_service(service_group_id)
        data = json.dumps(services_list)
        return HttpResponse(data, content_type='application/json')

    def _get_service(self, service_group_id):
        self.logger.info('========== Start Getting Services List ==========')
        if service_group_id == '-1':
            url = api_settings.GET_ALL_SERVICE_URL
        else:
            url = api_settings.GET_SERVICE_URL.format(serviceGroupId=service_group_id)
        service_list = self._get_method(url, "Get services list", logger, True)
        self.logger.info('========== Finish Getting Services List ==========')
        return service_list
