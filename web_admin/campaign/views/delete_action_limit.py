import logging

from authentications.utils import get_correlation_id_from_username
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_helper import RestfulHelper

from web_admin import setup_logger, api_settings

logger = logging.getLogger(__name__)


class DeleteActionLimitView(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        self.logger.info('========== Start deleting action limit ==========')
        campaign_id = context.get('campaign_id')
        mechanic_id = context.get('mechanic_id')
        action_id = context.get('action_id')
        action_limit_id = context.get('action_limit_id')
        is_success, status_message = self.__delete_action_limit(campaign_id, mechanic_id, action_id, action_limit_id)
        if is_success:
            self.logger.info('========== Finish deleting action limit ==========')
            messages.success(request, 'Delete successfully')
            return redirect('campaign:mechanic_detail', campaign_id=campaign_id, mechanic_id=mechanic_id)
        else:
            self.logger.info('========== Failed deleting action limit ==========')
            self.logger.info(status_message)
            messages.error(request, status_message)
            return redirect('campaign:mechanic_detail', campaign_id=campaign_id, mechanic_id=mechanic_id)

    def __delete_action_limit(self, campaign_id: int, mechanic_id: int, action_id: int, action_limit_id: int) -> tuple:
        url = api_settings.DELETE_LIMITATION.format(rule_id=campaign_id, mechanic_id=mechanic_id,
                                                    action_id=action_id, action_limit_id=action_limit_id)
        is_success, status_code, status_message, data = RestfulHelper.send('DELETE', url, {}, self.request,
                                                                           'Delete action limit')
        return is_success, status_message
