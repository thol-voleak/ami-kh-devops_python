from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

from django.views.generic.base import TemplateView
from django.conf import settings

import logging
import requests

logger = logging.getLogger(__name__)


class APIListView(TemplateView):
    template_name = 'api_management/api_list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting api List ==========')
        headers = get_auth_header(self.request.user)
        url = settings.DOMAIN_NAMES + settings.APIS_URL
        response = requests.get(url=url, headers=headers, verify=settings.CERT)
        logger.info('========== Finished getting api List ==========')
        json_data = response.json()
        data = json_data.get('data')
        logger.info("{}".format(response.content))
        status = json_data.get('status', {})
        if status.get('code', '') == "success":
            logger.info("response: {}".format(json_data))
            result = {'data': data.get('apis')}
            logger.info('========== End get order history list ==========')
            return result
        else:
            if status.get('code', '') == "access_token_expire":
                logger.info('========== End get order history list ==========')
                raise InvalidAccessToken(status.get('message', ''))

        raise Exception(response.content)
