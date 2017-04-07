from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header
from web_admin.utils import format_date_time

import requests
import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "service_group/service_group_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Service Group List ==========')
        data = self.get_service_group_list()
        refined_data = format_date_time(data)
        logger.info('========== Finished get Service Group List ==========')
        result = {'data': refined_data}
        return result

    def get_service_group_list(self):
        logger.info("Getting service group list by {} user id".format(self.request.user.username))
        headers = get_auth_header(self.request.user)
        url = settings.SERVICE_GROUP_LIST_URL
        logger.info("Getting service group list from backend with {} url".format(url))
        logger.info('Getting service group list from backend')
        auth_request = requests.get(url, headers=headers, verify=False)
        logger.info("Received data with response is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        data = json_data.get('data')

        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info("Response count is {}".format(len(data)))
                return data

        if json_data.get('message') == 'Unauthorized client or scope in request':
            raise Exception("{}".format(json_data.get('message')))

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))

