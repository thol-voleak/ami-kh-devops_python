import logging
import time

import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.http import HttpResponse

from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class AgentFeeView(TemplateView, GetHeaderMixin):

    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = settings.DOMAIN_NAMES + settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)
        logger.info('========== Start create Agent Hierarchy Fee ==========')
        logger.info('Username: {}, with url {}.'.format(self.request.user.username,url))

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "is_deleted": 0
        }


        logger.info("Request: {}".format(post_data))
        response = requests.post(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)

        logger.info("Response status: {}".format(response.status_code))
        logger.info("Response content: {}".format(response.content))
        if response.status_code == 200:
            messages.add_message(
                request,
                messages.INFO,
                'Added Agent Hierarchy Distribution - Fee successfully'
            )
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Something wrong happened!'
            )

        logger.info('========== Finish create Agent Hierarchy Fee list ==========')

        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=fee_tier_id)


class FeeDistributionsUpdate(View, GetHeaderMixin):

    def post(self, request, *args, **kwargs):
        logger.info("========== Start updating Agent Hierarchy Distribution - Fee ==========")
        logger.info("User: {}".format(self.request.user))

        fee_distributions_id = kwargs.get('fee_distributions_id')
        logger.info("updating Agent Hierarchy Distribution - Fee id: {}".format(fee_distributions_id))

        url = settings.DOMAIN_NAMES + settings.FEE_DISTRIBUTION_UPDATE_URL.format(fee_distributions_id=fee_distributions_id)
        logger.info("Url: {}".format(url))

        data = request.POST.copy()

        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get('sof_type_id'),
            "specific_sof": data.get("specific_sof"),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
        }
        logger.info("updating Agent Hierarchy Distribution - Fee request body: {}".format(post_data))
        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)
        done = time.time()

        logger.info("updating Agent Hierarchy Distribution - Fee response status: {}".format(response.status_code))
        logger.info("updating Agent Hierarchy Distribution - Fee response content: {}".format(response.content))
        logger.info("Response time: {} sec.".format(done - start_date))

        if response.status_code == 200:
            logger.info("updating Agent Hierarchy Distribution - Fee: row saving success!")
            httpResponse = HttpResponse(status=200, content=response)
        else:
            logger.info("updating Agent Hierarchy Distribution - Fee: Something wrong happened!")
            httpResponse = HttpResponse(status=response.status_code, content=response)

        logger.info("========== Finish updating Agent Hierarchy Distribution - Fee ==========")
        return httpResponse