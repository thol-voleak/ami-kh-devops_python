import requests
import logging
import time

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View
from web_admin.get_header_mixins import GetHeaderMixin


logger = logging.getLogger(__name__)


class DeleteCommand(View, GetHeaderMixin):
    def delete(self, request, *args, **kwargs):
        service_command_id = kwargs.get('service_command_id')
        logger.info('========== Start deleting Service Command ==========')
        success = self._delete_service_command(service_command_id)
        logger.info('========== Finish deleting Service Command ==========')

        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()


    def _delete_service_command(self, service_command_id):
        api_path = settings.SERVICE_COMMAND_DELETE_PATH.format(service_command_id)
        url = settings.DOMAIN_NAMES + api_path
        logger.info('API-Path: {};'.format(api_path))

        start_date = time.time()
        response = requests.delete(url, headers=self._get_headers(),
                                   verify=settings.CERT)
        done = time.time()
        logger.info('Reponse_time: {} sec.'.format(done - start_date))
        logger.info('Response_code: {};'.format(response.status_code))
        logger.info('Response_content: {};'.format(response.content))

        if response.status_code == 200:
            return True
        return False