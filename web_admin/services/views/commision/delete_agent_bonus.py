import logging
from django.conf import settings
from web_admin import api_settings
from django.views.generic.base import View
from web_admin.utils import setup_logger
from web_admin import ajax_functions
logger = logging.getLogger(__name__)

class DeleteAgentBonus(View):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(DeleteAgentBonus, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting Agent Bonus ==========')
        agent_bonus_distribution_id = kwargs.get('agent_bonus_distribution_id')
        api_path = api_settings.AGENT_BONUS_DELETE_PATH.format(
            agent_bonus_distribution_id=agent_bonus_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path

        response = ajax_functions._delete_method(request, url, "", logger)
        self.logger.info('========== Finish deleting Agent Bonus ==========')
        return response

