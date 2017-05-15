from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging
import requests

logger = logging.getLogger(__name__)


class APIListView(TemplateView):
    template_name = 'api_management/list_api.html'
    response = {}

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting api List ==========')

        headers = get_auth_header(self.request.user)
        url = settings.DOMAIN_NAMES + settings.APIS_URL
        response = requests.get(url=url, headers=headers, verify=settings.CERT)
        logger.info('========== Finished getting api List ==========')
        json_data = response.json()
        data = json_data.get('data')

        status = json_data.get('status', {})
        if status.get('code', '') == "success":
            self.response["data"] = data.get('apis')
            logger.info("All api is {} apis".format(len(data.get('apis'))))
            logger.info('========== End get all api list ==========')
            return self.response
        else:
            if status.get('code', '') == "access_token_expire":
                logger.info('========== End get all api list ==========')
                raise InvalidAccessToken(status.get('message', ''))

        raise Exception(response.content)


class AddAPIView(TemplateView):
    template_name = 'api_management/add_api.html'
    choices = {"GET", "POST", "PUT", "DELETE"}
    boolean_list = {"true", "false"}
    data = {}

    def get_context_data(self, **kwargs):
        self.data["choices"] = self.choices
        self.data["services"] = self._get_services_list()
        self.data["boolean_list"] = self.boolean_list
        return self.data

    def _get_services_list(self):
        if getattr(self, '_services', None) is None:
            logger.info("Getting service list by {} user id".format(self.request.user.username))
            headers = get_auth_header(self.request.user)
            url = settings.DOMAIN_NAMES + settings.SERVICES_LIST_URL

            logger.info("Getting service list from backend with {} url".format(url))
            response = requests.get(url, headers=headers, verify=settings.CERT)
            logger.info("Get service list response status is {}".format(response.status_code))
            logger.info("Get service list response data is {}".format(response.content))

            json_data = response.json()
            data = json_data.get('data')

            if response.status_code == 200 and json_data["status"]["code"] == 'success':
                logger.info('Service count: {}'.format(len(data)))
                self._services_list = data.get("services", {})

            elif json_data["status"]["code"] == "access_token_expire":
                logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
                raise InvalidAccessToken(json_data["status"]["message"])
        return self._services_list

    def post(self, request, *args, **kwargs):
        logger.info('========== Start post add new api ==========')
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
        
        headers = get_auth_header(self.request.user)
        url = settings.DOMAIN_NAMES + settings.APIS_URL

        response = requests.post(url=url, json=data, headers=headers, verify=settings.CERT)
        json_data = response.json()

        if response.status_code == 200 and json_data["status"]["code"] == 'success':
            logger.info("Add new api success with {} name".format(api_name))
            logger.info('========== End post add new api ==========')
            return redirect('api_management:api_list')

        elif json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])


class ServiceListView(TemplateView):
    template_name = 'api_management/service_list.html'
    response = {}

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting api List ==========')

        headers = get_auth_header(self.request.user)
        url = settings.DOMAIN_NAMES + settings.APIS_URL
        response = requests.get(url=url, headers=headers, verify=settings.CERT)
        logger.info('========== Finished getting api List ==========')
        json_data = response.json()
        data = json_data.get('data')

        status = json_data.get('status', {})
        if status.get('code', '') == "success":
            self.response["data"] = data.get('apis')
            logger.info("All api is {} apis".format(len(data.get('apis'))))
            logger.info('========== End get all api list ==========')
            return self.response
        else:
            if status.get('code', '') == "access_token_expire":
                logger.info('========== End get all api list ==========')
                raise InvalidAccessToken(status.get('message', ''))

        raise Exception(response.content)
