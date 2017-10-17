from braces.views import GroupRequiredMixin
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from authentications.apps import InvalidAccessToken
from django.contrib import messages
from web_admin.api_settings import DELETE_AGENT_SMART_CARD_PATH
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class SmartCardDelete(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_DELETE_AGENT_SMARTCARD"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/smart_card.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SmartCardDelete, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(SmartCardDelete, self).get_context_data(**kwargs)
        self.logger.info('========== Start deleting agent smartcard ==========')
        agent_id = context.get('agent_id')
        smartcard_id = context.get('smartcard_id')

        url = DELETE_AGENT_SMART_CARD_PATH.format(agent_id, smartcard_id)

        success, status_code, message = RestFulClient.delete(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
        )

        API_Logger.delete_logging(loggers=self.logger,
                                  status_code=status_code)

        self.logger.info('========== Finished deleting agent smartcard ==========')
        if success:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                'Delete agent smartcard successfully'
            )
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{} for {} username".format(message, self.request.user))
            raise InvalidAccessToken(message)
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                "Got error and can't delete smartcard"
            )

        return redirect('agents:agent-smartcard', agent_id=agent_id)