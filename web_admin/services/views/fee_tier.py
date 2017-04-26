import logging
import time

import requests
from django.conf import settings
from django.http import Http404
from django.views.generic.base import TemplateView

from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import format_date_time

logger = logging.getLogger(__name__)


class FeeTierListView(TemplateView, GetHeaderMixin):

    template_name = "services/fee_tier.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FeeTierListView, self).get_context_data(*args, **kwargs)
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')
        if not service_id or not service_command_id:
            raise Http404

        logger.info('========== Start get Fee Tier List ==========')
        data, success = self._get_fee_tier_list(service_command_id)
        logger.info('========== Finished get Fee Tier List ==========')

        if success:
            data = format_date_time(data)

        context['data'] = data
        context['msg'] = self.request.session.pop('add_tier_msg', None)
        context['edit_msg'] = self.request.session.pop('edit_tier_msg', None)

        logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        logger.info('========== Finish get service name ==========')

        logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        logger.info('========== Finish get command name ==========')

        return context

    def _get_fee_tier_list(self, service_command_id):
        logger.info("Getting fee tier list by user: {}".format(self.request.user.username))

        url = settings.FEE_TIER_LIST.format(service_command_id=service_command_id)
        logger.info("Getting fee tier list from backend with url: {}".format(url))

        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        logger.info('Status code: {}'.format(response.status_code))

        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get('data', [])
            logger.info('Fee tier count: {}'.format(len(data)))
            return data, True
        else:
            logger.info('Response content: {}'.format(response.content))
            return [], False

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
