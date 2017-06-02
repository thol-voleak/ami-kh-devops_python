import logging

from web_admin import api_settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View
from django.http import Http404
from multiprocessing.pool import ThreadPool
from web_admin.restful_methods import RESTfulMethods
from web_admin import ajax_functions
from services.views.mixins import GetCommandNameAndServiceNameMixin

logger = logging.getLogger(__name__)




class FeeDistributionsUpdate(View):

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

        response = ajax_functions._put_method(request, url, "", logger, post_data)
        logger.info("========== Finish updating Agent Hierarchy Distribution - Fee ==========")
        return response