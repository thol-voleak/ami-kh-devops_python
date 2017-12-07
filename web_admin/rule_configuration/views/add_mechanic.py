from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC
from web_admin import setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin import api_settings
import logging


logger = logging.getLogger(__name__)

class AddMechanic(TemplateView, GetHeaderMixin):
    group_required = "CAN_CREATE_RULE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = 'rule_configuration/add_mechanic.html'
    path = api_settings.CREATE_RULE
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddMechanic, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== User go to Add Mechanic page ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        context['dtp_start_date'] = datetime.now().strftime("%Y-%m-%d")
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding Mechanic ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        rule_id = context['rule_id']
        triger = request.POST.get('trigger')
        input_start_date = request.POST.get('dtp_start_date')
        input_end_date = request.POST.get('dtp_end_date')
        input_start_time = request.POST.get('dtp_start_time')
        input_end_time = request.POST.get('dtp_end_time')

        start_hour = int(input_start_time[0:2])
        start_minute = int(input_start_time[-2:])
        start_date = datetime.strptime(input_start_date, "%Y-%m-%d")
        start_date = start_date.replace(hour=start_hour, minute=start_minute,
                                        second=0)
        param_start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        params = {
            "event_name": triger,
            "start_timestamp": param_start_date,
        }
        if input_end_date:
            end_date = datetime.strptime(input_end_date, "%Y-%m-%d")
            if input_end_time:
                end_hour = int(input_end_time[0:2])
                end_minute = int(input_end_time[-2:])
            else:
                end_hour = 0
                end_minute = 1
            end_date = end_date.replace(hour=end_hour, minute=end_minute, second=0)
            param_end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            params["end_timestamp"] = param_end_date

        success, status_code, message, data = RestFulClient.post(
            url=CREATE_MECHANIC.format(rule_id=rule_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params,
                                response=data, status_code=status_code)

        self.logger.info('========== Finish adding Mechanic ==========')

        if success:
            return redirect('rule_configuration:add_condition', rule_id=rule_id, mechanic_id=data['id'])
        else:
            context['dtp_start_time'] = input_start_time
            context['dtp_end_time'] = input_end_time
            context['dtp_start_date'] = input_start_date
            context['dtp_end_date'] = input_end_date
            context['trigger'] = triger
            if message == 'Invalid date time':
                error_msg = 'End Date could not be less than Start Date, and Start date and End date should be within range of this Rule'
            else:
                error_msg = message
            messages.add_message(
                request,
                messages.ERROR,
                error_msg
            )
            return render(request, self.template_name, context=context)