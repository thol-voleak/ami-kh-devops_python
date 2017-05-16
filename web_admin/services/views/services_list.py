from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

import requests
import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "services/services_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Service List ==========')
        data = self.get_services_list()
        logger.info('========== Finished get Service List ==========')
        result = {'data': data}
        return result

    def get_services_list(self):
        logger.info("Getting service list by {} user id".format(self.request.user.username))
        headers = get_auth_header(self.request.user)
        url = settings.SERVICE_LIST_URL

        logger.info("Getting service list from backend with {} url".format(url))
        auth_request = requests.get(url, headers=headers, verify=settings.CERT)
        logger.info("Get service list response status is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        status = json_data.get('status', {})
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)
        data = json_data.get('data')

        if auth_request.status_code == 200 and json_data["status"]["code"] == 'success':
            logger.info('Service count: {}'.format(len(data)))
            return data

        elif json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])

        else:
            raise Exception("{}".format(json_data["status"]["message"]))
