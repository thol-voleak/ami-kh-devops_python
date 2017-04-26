import logging
import time

import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic.base import View

from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class AgentBonusDistributions(View, GetHeaderMixin):
    def post(self, request, *args, **kwargs):
        logger.info('========== Start add agent hierarchy distribution bonus ==========')
        service_id = kwargs.get('service_id')
        tf_fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')
        url = settings.DOMAIN_NAMES + settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id)

        logger.info('API-Path for add agent hierarchy distribution bonus is {}'.format(url))

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
        }

        logger.info("Params for add agent hierarchy distribution bonus is {}".format(post_data))
        start_date = time.time()
        response = requests.post(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)
        done = time.time()
        logger.info("Response status for add agent hierarchy distribution bonus is {}".format(response.status_code))
        logger.info("Response body for add agent hierarchy distribution bonus is {}".format(response.content))

        response_json = response.json()
        if response.status_code == 200 and response_json['status']['code'] == "success":
            messages.add_message(
                request,
                messages.INFO,
                'Added Agent Hierarchy Distribution - Bonus Successfully'
            )
        else:
            logger.info("Response body for add agent hierarchy distribution bonus is {}".format(response.content))
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )
        logger.info('Response time for add agent hierarchy distribution bonus is {} sec.'.format(done - start_date))
        logger.info('========== Finish add agent hierarchy distribution bonus  ==========')
        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=tf_fee_tier_id)


class AgentFeeHierarchyDistributionsDetail(View, GetHeaderMixin):

    def delete(self, request, *args, **kwargs):
        agent_fee_distribution_id = kwargs.get('agent_fee_distribution_id')

        logger.info('========== Start delete Agent Fee Hierarchy ==========')
        success = self._delete_agent_distribution(agent_fee_distribution_id)
        logger.info('========== Finish delete Agent Fee Hierarchy ==========')

        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()

    def _delete_agent_distribution(self, agent_fee_distribution_id):
        api_path = settings.AGENT_FEE_DISTRIBUTION_DETAIL_URL.format(
            agent_fee_distribution_id=agent_fee_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path
        logger.info('API-Path: {path}'.format(path=api_path))
        start_date = time.time()
        response = requests.delete(url, headers=self._get_headers(),
                                   verify=settings.CERT)
        done = time.time()
        logger.info('Reponse_time: {} sec.'.format(done - start_date))
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.content))

        if response.status_code == 200:
            return True
        return False
