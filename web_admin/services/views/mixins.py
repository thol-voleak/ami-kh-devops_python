import logging
import time
import requests


from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings

logger = logging.getLogger(__name__)

    
class GetCommandNameAndServiceNameMixin(GetHeaderMixin):

    def _get_command_name_by_id(self, command_id):
        url = settings.COMMAND_LIST_URL
        logger.info('URL: {}'.format(url))
        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(),
                                verify=settings.CERT)
        done = time.time()
        logger.info('Reponse time: {} sec.'.format(done - start_date))
        logger.info('Response code: {}'.format(response.status_code))
        logger.info('Response content: {}'.format(response.content))

        json_response = response.json()
        if response.status_code == 200 and json_response['status']['code'] == 'success':
            data = json_response['data']
            command_name =  [d['command_name']
                             for d in data
                             if str(d['command_id']) == str(command_id)]
            if command_name:
                return command_name[0]
        return command_id

    def _get_service_name_by_id(self, service_id):
        url = settings.SERVICE_DETAIL_URL.format(service_id)
        logger.info('URL: {}'.format(url))
        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(),
                                verify=settings.CERT)
        done = time.time()
        logger.info('Reponse time: {} sec.'.format(done - start_date))
        logger.info('Response code: {}'.format(response.status_code))
        logger.info('Response content: {}'.format(response.content))

        json_response = response.json()
        if response.status_code == 200 and json_response['status']['code'] == 'success':
            data = json_response['data']
            return data['service_name']
        return service_id