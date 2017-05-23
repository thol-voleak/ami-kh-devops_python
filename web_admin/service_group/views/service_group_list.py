from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

import requests
import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "service_group/service_group_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Service Group List ==========')
        data = self.get_service_group_list()
        logger.info('========== Finished get Service Group List ==========')
        result = {'data': data}
        return result

    def get_service_group_list(self):
        logger.info("Getting service group list by {} user id".format(self.request.user.username))
        headers = get_auth_header(self.request.user)
        url = settings.DOMAIN_NAMES + settings.SERVICE_GROUP_LIST_URL
        logger.info("Getting service group list from backend with {} url".format(url))
        logger.info('Getting service group list from backend')
        response = requests.get(url, headers=headers, verify=settings.CERT)
        logger.info("Received data with response is {}".format(response.status_code))

        response_json = response.json()
        status = response_json.get('status', {})
        # if not isinstance(status, dict):
        #     status = {}
        code = status.get('code', '')

        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data', [])
            logger.info("Response count is {}".format(len(data)))
        else:
            data = []
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        return data
