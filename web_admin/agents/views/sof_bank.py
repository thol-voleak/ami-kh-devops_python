from braces.views import GroupRequiredMixin

from authentications.apps import InvalidAccessToken
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from django.contrib import messages
from web_admin.api_settings import LIST_BANK_SOFS_URL
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from django.conf import settings
import logging


logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class SOFBankView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_VIEW_AGENT_SOFBANK"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/agent_sof_bank_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SOFBankView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting list agent sof bank ==========')
        context = super(SOFBankView, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        data = self._get_agent_sof_bank(agent_id)
        context = {
            "data": data["bank_sofs"],
            'agent_id': agent_id,
        }
        self.logger.info('========== Finished getting agent sof bank ==========')
        return render(request, self.template_name, context)

    def _get_agent_sof_bank(self, agent_id):
        params = {"user_id": agent_id}
        is_success, status_code, status_message, data = RestFulClient.post(url=LIST_BANK_SOFS_URL, params=params,
                                                                           loggers=self.logger,
                                                                           headers=self._get_headers(),
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data



