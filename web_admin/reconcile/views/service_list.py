import logging
import json
from django.http import HttpResponseRedirect, HttpResponse
from reconcile.views.partner_file_list import PartnerFileList
from web_admin import api_settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger

logger = logging.getLogger(__name__)

class ServiceList(TemplateView, RESTfulMethods):

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ServiceList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        service_group_id = request.GET.get('service_group_id')
        d = self._get_service(service_group_id)
        data = json.dumps(d)
        return HttpResponse(data, content_type='application/json')

    def _get_service(self, service_group_id):
        if service_group_id == '-1':
            url = api_settings.GET_ALL_SERVICE_URL
            return self._get_method(url, "services", logger, True)
        url = api_settings.GET_SERVICE_URL
        url = url.replace("{service_group_id}", service_group_id)
        return self._get_method(url, "services", logger, True)
