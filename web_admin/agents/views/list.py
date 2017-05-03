import requests
import logging
import time

from django.conf import settings
from django.views.generic.base import TemplateView

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

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info('Agent count: {};'.format(len(data)))
                return data

        if auth_request.status_code == 200:
            json_data = auth_request.json()
            data = json_data.get('data', [])
            logger.info('Agent_count: {}'.format(len(data)))
            return data, True
        else:
            logger.info('Response_content: {}'.format(auth_request.content))
            return [], False

    def format_data(self, data):
        for i in data:
            i['kyc_status'] = KYC.get(i['kyc_status'])
            i['status'] = STATUS.get(i['status'])
        return data