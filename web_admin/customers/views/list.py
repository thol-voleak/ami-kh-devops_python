import requests
import logging
import time

from django.conf import settings
from authentications.apps import InvalidAccessToken
from django.views.generic.base import TemplateView

from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)

class ListView(TemplateView, GetHeaderMixin):
    template_name = 'member_customer_list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting Customer List ==========')
        customer_list = self.get_member_customer_list()
        logger.info('========== Finished getting Customer List ==========')
        result = {'data': customer_list}
        return result

    def get_member_customer_list(self):
        api_path = settings.MEMBER_CUSTOMER_PATH
        url = settings.DOMAIN_NAMES + api_path

        logger.info('API-Path: {};'.format(api_path))
        body = {}

        start = time.time()
        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {};".format(response.status_code))
        logger.info("Response_time: {} sec.".format(end - start))

        response_json = response.json()

        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')

        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data', [])
            logger.info('Customer list count: {};'.format(len(data)))
        else:
            data = []
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        return data