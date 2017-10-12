from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from django.contrib import messages
from web_admin.api_settings import AGENT_SMARTCARD_PATH
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class SmartCardView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_AGENT_SMARTCARD"
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
        return super(SmartCardView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting list agent smart card ==========')
        context = super(SmartCardView, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        agent_smartcard = self._get_agent_smartcard(agent_id)

        context = {
            "smartcards": agent_smartcard,
        }
        self.logger.info('========== Finished getting agent smartcard ==========')
        return render(request, self.template_name, context)

    def _get_agent_smartcard(self, agent_id):
        params = {"agent_id": agent_id}
        is_success, status_code, status_message, data = RestFulClient.post(url=AGENT_SMARTCARD_PATH,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data