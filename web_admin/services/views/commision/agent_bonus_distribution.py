from authentications.utils import get_correlation_id_from_username
from web_admin import api_settings
from web_admin import ajax_functions
from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import View

import logging

logger = logging.getLogger(__name__)


class AgentFeeHierarchyDistributionsDetail(View, RESTfulMethods):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentFeeHierarchyDistributionsDetail, self).dispatch(request, *args, **kwargs)


def delete(self, request, *args, **kwargs):
    agent_fee_distribution_id = kwargs.get('agent_fee_distribution_id')

    self.logger.info('========== Start deleting Agent Hirarchy Distribution - Fee ==========')

    url = api_settings.AGENT_FEE_DISTRIBUTION_DETAIL_URL.format(agent_fee_distribution_id=agent_fee_distribution_id)

    response = ajax_functions._delete_method(request, url, "", self.logger)
    self.logger.info('========== Finish deleting Agent Hirarchy Distribution - Fee ==========')
    return response
