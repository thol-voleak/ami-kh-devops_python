from braces.views import GroupRequiredMixin

from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.contrib import messages

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class MechanicDelete(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_DELETE_MECHANIC"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(MechanicDelete, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(MechanicDelete, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        mechanic_id = context['mechanic_id']

        url = api_settings.DELETE_MECHANIC_URL.format(campaign_id=campaign_id, mechanic_id=mechanic_id)

        self.logger.info('========== Start  Deleting  Mechanic ==========')

        is_success, status_code, status_message = RestFulClient.delete(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={},response={},
                               status_code=status_code)
        if is_success:
            self.logger.info('========== Finish  Deleting  Mechanic ==========')
            messages.success(request, 'Mechanic Deleted')
            return redirect('campaign:campaign_detail', campaign_id=campaign_id)
        else:
            self.logger.info('========== Finish  Deleting  Mechanic ==========')
            return redirect('campaign:campaign_detail', campaign_id=campaign_id)


