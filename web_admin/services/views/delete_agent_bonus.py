import logging
import time
import requests
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View
from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class DeleteAgentBonus(View, GetHeaderMixin):
    def delete(self, request, *args, **kwargs):
        agent_bonus_distribution_id = kwargs.get('agent_bonus_distribution_id')
        logger.info('========== Start delete Agent Bonus on commission and payment method ==========')
        success = self._delete_agent_bonus(agent_bonus_distribution_id)
        logger.info('========== Finish delete Agent Bonus on commission and payment method ==========')
        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()

    def _delete_agent_bonus(self, agent_bonus_distribution_id):
        api_path = settings.AGENT_BONUS_DELETE_PATH.format(
            agent_bonus_distribution_id=agent_bonus_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path
        logger.info('API-Path: {path}'.format(path=api_path))

        start_date = time.time()
        response = requests.delete(url, headers=self._get_headers(),
                                   verify=settings.CERT)
        done = time.time()
        logger.info('Response_time: {} sec.'.format(done - start_date))
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.content))

        if response.status_code == 200:
            return True
        return False
