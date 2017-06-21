import logging

from web_admin import api_settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import View, TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin import ajax_functions
from multiprocessing.pool import ThreadPool
logger = logging.getLogger(__name__)
from services.views.mixins import GetCommandNameAndServiceNameMixin
from web_admin.utils import setup_logger


class AgentFeeHierarchyDistributionsDetail(View, RESTfulMethods):
	logger = logger

	def dispatch(self, request, *args, **kwargs):
		self.logger = setup_logger(self.request, logger)
		return super(AgentFeeHierarchyDistributionsDetail, self).dispatch(request, *args, **kwargs)

	def delete(self, request, *args, **kwargs):
		agent_fee_distribution_id = kwargs.get('agent_fee_distribution_id')

		self.logger.info('========== Start deleting Agent Hirarchy Distribution - Fee ==========')

		url=api_settings.AGENT_FEE_DISTRIBUTION_DETAIL_URL.format(agent_fee_distribution_id=agent_fee_distribution_id)

		response = ajax_functions._delete_method(request, url, "", logger)
		self.logger.info('========== Finish deleting Agent Hirarchy Distribution - Fee ==========')
		return response
