import logging

from web_admin import api_settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic.base import View

from web_admin.restful_methods import RESTfulMethods
from web_admin import ajax_functions

logger = logging.getLogger(__name__)


class AgentBonusDistributions(View, RESTfulMethods):
    def post(self, request, *args, **kwargs):
        logger.info('========== Start add agent hierarchy distribution bonus ==========')
        service_id = kwargs.get('service_id')
        tf_fee_tier_id = kwargs.get('fee_tier_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')
        url = api_settings.AGENT_BONUS_DISTRIBUTION_URL.format(tf_fee_tier_id=tf_fee_tier_id)

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

        response, status = self._post_method(api_path=url,
                                   func_description="Add Agent Hierarchy Distribution Bonus",
                                   logger=logger, params=post_data)

        if status:
            messages.add_message(
                request,
                messages.INFO,
                'Added Agent Hierarchy Distribution - Bonus Successfully'
            )
        else:
            logger.info("Response body for add agent hierarchy distribution bonus is {}".format(response))
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


class AgentFeeHierarchyDistributionsDetail(View):

    def delete(self, request, *args, **kwargs):
        agent_fee_distribution_id = kwargs.get('agent_fee_distribution_id')

        logger.info('========== Start deleting Agent Hirarchy Distribution - Fee ==========')
    #     success = self._delete_agent_distribution(agent_fee_distribution_id)
    #
    #
    #     if success:
    #         return HttpResponse(status=204)
    #     return HttpResponseBadRequest()
    #
    # def _delete_agent_distribution(self, agent_fee_distribution_id):
    #
    #     data, success = self._delete_method(
        url=api_settings.AGENT_FEE_DISTRIBUTION_DETAIL_URL.format(agent_fee_distribution_id=agent_fee_distribution_id)
    #         func_description="Delete Agent Distribution",
    #         logger=logger)
    #     return success

        response = ajax_functions._delete_method(request, url, "", logger)
        logger.info('========== Finish deleting Agent Hirarchy Distribution - Fee ==========')
        return response
