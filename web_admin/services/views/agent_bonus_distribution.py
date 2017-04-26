from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from authentications.utils import get_auth_header

import logging
import requests
import time

from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import format_date_time

logger = logging.getLogger(__name__)


class AgentBonusDistributions(View, GetHeaderMixin):
    def post(self, request, *args, **kwargs):
        logger.info('========== Start add agent hierarchy distribution bonus ==========')
        service_id = kwargs.get('service_id')
        tf_fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')
        url = settings.DOMAIN_NAMES + settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id)

        logger.info('Add agent hierarchy distribution bonus url id {}'.format(self.request.user.username, url))

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id", "")
        }

        logger.info("Request data for add agent hierarchy distribution bonus {}".format(post_data))
        start_date = time.time()
        response = requests.post(url, headers=self._get_headers(), json=post_data, verify=settings.CERT)
        done = time.time()
        logger.info('Response time for add agent hierarchy distribution bonus is {} s.'.format(done - start_date))
        logger.info("Response status for add agent hierarchy distribution bonus is {}".format(response.status_code))

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

        logger.info('========== Finish add agent hierarchy distribution bonus  ==========')
        return redirect('services:commission_and_payment',
                        service_id=service_id,
                        command_id=command_id,
                        service_command_id=service_command_id,
                        fee_tier_id=tf_fee_tier_id)
