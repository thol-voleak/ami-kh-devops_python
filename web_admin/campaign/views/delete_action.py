import logging

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient

from web_admin import api_settings, setup_logger

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class ActionDelete(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ActionDelete, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ActionDelete, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        mechanic_id = context['mechanic_id']
        action_id = context['action_id']

        url = api_settings.DELETE_ACTION.format(rule_id=campaign_id, mechanic_id=mechanic_id, action_id=action_id)

        self.logger.info('========== Start  Deleting  Action ==========')

        is_success, status_code, status_message = RestFulClient.delete(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={},response={},
                               status_code=status_code)
        if is_success:
            self.logger.info('========== Finish  Deleting  Action ==========')
            messages.success(request, 'Delete successfully')
            return redirect('campaign:mechanic_detail', campaign_id=campaign_id, mechanic_id=mechanic_id)
        else:
            self.logger.info('========== Failed  Deleting  Action ==========')
            self.logger.info(status_message)
            messages.error(request, status_message)
            return redirect('campaign:mechanic_detail', campaign_id=campaign_id, mechanic_id=mechanic_id)


