from web_admin.restful_methods import RESTfulMethods
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
import logging
from authentications.utils import get_correlation_id_from_username


logger = logging.getLogger(__name__)


class APIListView(TemplateView, RESTfulMethods):
    template_name = 'api_management/list_api.html'
    logger = logger
    response = {}
    
    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(APIListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting api List ==========')
        url = api_settings.APIS_URL
        data, success = self._get_method(url, "service list", logger)
        self.logger.info('========== Finished getting api List ==========')
        self.response["data"] = data.get('apis', [])
        return self.response


class AddAPIView(TemplateView, RESTfulMethods):
    template_name = 'api_management/add_api.html'
    logger = logger
    choices = {"GET", "POST", "PUT", "DELETE"}
    boolean_list = {"true", "false"}
    data = {}

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddAPIView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.data["choices"] = self.choices
        self.data["services"] = self._get_services_list()
        self.data["boolean_list"] = self.boolean_list
        return self.data

    def _get_services_list(self):
        if getattr(self, '_services', None) is None:
            self.logger.info("Getting service list by {} user id".format(self.request.user.username))
            url = api_settings.SERVICES_LIST_URL
            data, success = self._get_method(url, "service list", logger)
            self._services_list = data.get("services", [])

        return self._services_list

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start post add new api ==========')
        api_name = request.POST.get('api_name')
        api_http_method = request.POST.get('api_http_method')
        api_pattern = request.POST.get('api_pattern')
        is_internal = request.POST.get('is_internal')
        is_required_access_token = request.POST.get('is_required_access_token')
        prefix = request.POST.get('prefix')
        service_id = request.POST.get('service_id')

        data = {
            "name": api_name,
            "http_method": api_http_method,
            "pattern": api_pattern,
            "is_internal": is_internal,
            "is_required_access_token": is_required_access_token,
            "service_id": service_id,
            "prefix": prefix
        }
        
        url = api_settings.APIS_URL
        data, success = self._post_method(url, "API", logger, data)
        self.logger.info('========== End post add new api ==========')
        if success:
            return redirect('api_management:api_list')


class ServiceListView(TemplateView, RESTfulMethods):
    template_name = 'api_management/service_list.html'
    logger = logger
    response = {}

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ServiceListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting api List ==========')
        url = api_settings.APIS_URL
        data, success = self._get_method(url, "api List", logger)

        self.response["data"] = data.get('apis', [])
        self.logger.info('========== Finish getting api List ==========')
        return self.response


