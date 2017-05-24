import logging
from django.conf import settings
from web_admin import api_settings
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic.base import View
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class DeleteAgentBonus(View, RESTfulMethods):
    def delete(self, request, *args, **kwargs):
        agent_bonus_distribution_id = kwargs.get('agent_bonus_distribution_id')
        data, success = self._delete_agent_bonus(agent_bonus_distribution_id)
        if success:
            return HttpResponse(status=204)
        return HttpResponseBadRequest()

    def _delete_agent_bonus(self, agent_bonus_distribution_id):
        api_path = api_settings.AGENT_BONUS_DELETE_PATH.format(
            agent_bonus_distribution_id=agent_bonus_distribution_id
        )
        url = settings.DOMAIN_NAMES + api_path
        return self._delete_method(url, "Agent Bonus on commission and payment", logger)

