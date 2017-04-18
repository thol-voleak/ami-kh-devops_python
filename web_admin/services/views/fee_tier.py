import logging

import requests
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views.generic.base import TemplateView

from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import format_date_time

logger = logging.getLogger(__name__)


class FeeTierListView(TemplateView, GetHeaderMixin):

    template_name = "services/fee_tier.html"

    def get(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        if not service_id or not command_id:
            raise Http404

        service_command_id = self._get_service_command(service_id, command_id)
        if service_command_id is None:
            raise Http404

        logger.info('========== Start get Fee Tier List ==========')
        data, success = self._get_fee_tier_list(service_command_id)
        logger.info('========== Finished get Fee Tier List ==========')

        if success:
            data = format_date_time(data)

        return render(request, self.template_name, {'data': data,
                                                    'service_id': service_id,
                                                    'command_id': command_id})

    def _get_service_command(self, service_id, command_id):
        url = settings.COMMAND_LIST_BY_SERVICE_URL.format(service_id)
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)

        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get('data', [])
            data = filter(lambda x: str(x['command_id']) == command_id, data)
            for d in data:
                return d['service_command_id']
        return None

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
