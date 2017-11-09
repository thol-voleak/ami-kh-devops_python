from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC
from web_admin import setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from datetime import datetime
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AddMechanic(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_VIEW_CAMPAIGN_DETAILS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "campaign/add_mechanic.html"
    logger = logger

    permission_required = "auth.change_user"
    login_url = settings.LOGIN_URL
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddMechanic, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Add Mechanic page ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        context['dtp_start_date'] = datetime.now().strftime("%Y-%m-%d")
        context['dtp_end_date'] = datetime.now().strftime("%Y-%m-%d")
        self.logger.info('========== Finished showing Add Mechanic page ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding Mechanic ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        str_start_date = request.POST.get('dtp_start_date')
        str_end_date = request.POST.get('dtp_end_date')
        start_time = request.POST.get('dtp_start_time')
        end_time = request.POST.get('dtp_start_time')
        start_hour = int(start_time[0:2])
        start_minute = int(start_time[-2:])
        end_hour = int(end_time[0:2])
        end_minute = int(end_time[-2:])
        if str_start_date:
            start_date = datetime.strptime(str_start_date, "%Y-%m-%d")
        else:
            start_date = datetime.now()

        start_date = start_date.replace(hour=start_hour, minute=start_minute, second=0)
        start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        if str_end_date:
            end_date = datetime.strptime(str_end_date, "%Y-%m-%d")
        else:
            end_date = datetime.now()

        end_date = end_date.replace(hour=end_hour, minute=end_minute, second=0)
        end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        params = {
            "event_name": request.POST.get('trigger'),
            "start_timestamp": start_date,
            "end_timestamp": end_date
        }

        success, status_code, message, data = RestFulClient.post(
            url=CREATE_MECHANIC.format(rule_id=campaign_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)
        if success:
            messages.success(request, 'A mechanic is created successfully')
            return redirect('campaign:campaign_detail',campaign_id=campaign_id)
