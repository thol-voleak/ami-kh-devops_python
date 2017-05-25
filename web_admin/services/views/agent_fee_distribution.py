import logging
import json

from web_admin import api_settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.http import HttpResponse

from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class AgentFeeView(TemplateView, RESTfulMethods):

    def post(self, request, *args, **kwargs):
        service_id = kwargs.get('service_id')
        fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')

        url = api_settings.AGENT_FEE_DISTRIBUTION_URL.format(fee_tier_id=fee_tier_id)
        logger.info('========== Start create Agent Hierarchy Fee ==========')

        data = request.POST.copy()
        post_data = {
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get("sof_type_id"),
            "specific_sof": data.get('specific_sof'),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
            "is_deleted": 0
        }

        if post_data['actor_type'] != 'Specific ID':
            post_data['specific_actor_id'] = ''

        response, status = self._post_method(api_path=url,
                                       func_description="create Agent Hierarchy Fee",
                                       logger=logger, params=post_data)

        if status:
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


class FeeDistributionsUpdate(View, RESTfulMethods):

    def post(self, request, *args, **kwargs):

        logger.info("========== Start updating Agent Hierarchy Distribution - Fee ==========")

        agent_fee_distribution_id = kwargs.get('fee_distributions_id')
        url = api_settings.AGENT_FEE_DISTRIBUTION_DETAIL_URL.format(agent_fee_distribution_id=agent_fee_distribution_id)

        data = request.POST.copy()

        post_data = {
            "fee_tier_id": data.get("fee_tier_id"),
            "action_type": data.get("action_type"),
            "actor_type": data.get("actor_type"),
            "sof_type_id": data.get('sof_type_id'),
            "specific_sof": data.get("specific_sof"),
            "amount_type": data.get("amount_type"),
            "rate": data.get("rate"),
            "specific_actor_id": data.get("specific_actor_id"),
        }

        response, status = self._put_method(api_path=url,
                                  func_description="updating Agent Hierarchy Distribution - Fee",
                                  logger=logger, params=post_data)


        response = json.dumps({"status": {"code": "success", "message": "Success"}, "data": response})
        if status:
            httpResponse = HttpResponse(status=200, content=response)
        else:
            httpResponse = HttpResponse(status=400, content=response)

        logger.info("========== Finish updating Agent Hierarchy Distribution - Fee ==========")
        return httpResponse