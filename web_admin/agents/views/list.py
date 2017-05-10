import requests
import logging
import time

from django.conf import settings
from django.views.generic.base import TemplateView
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)

STATUS = {
    1: 'Active',
}

KYC = {
    True: 'YES',
    False: 'NO',
}

class ListView(TemplateView):
    template_name = 'list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting Agent List ==========')
        data = self.get_agent_list()
        logger.info('========== Finished getting Agent List ==========')
        result = {'data': self.format_data(data)}
        return result

    def get_agent_list(self):
        url = settings.DOMAIN_NAMES + settings.AGENT_LIST_PATH

        logger.info('API-Path: {};'.format(settings.AGENT_LIST_PATH))
        start = time.time()
        auth_request = requests.get(url, headers=get_auth_header(self.request.user),
                                    verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {};".format(auth_request.status_code))
        logger.info("Response_time: {} sec.".format(end - start))

        response_json = auth_request.json()
        status = response_json.get('status', {})
        # if not isinstance(status, dict):
        #     status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data', [])
            logger.info('Agent count: {};'.format(len(data)))
        else:
            data = []
            logger.info('get_agent_list Response_content: {}'.format(auth_request.text))
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

        return data


    def format_data(self, data):
        for i in data:
            i['kyc_status'] = KYC.get(i.get('kyc_status'))
            i['status'] = STATUS.get(i.get('status'))
        return data