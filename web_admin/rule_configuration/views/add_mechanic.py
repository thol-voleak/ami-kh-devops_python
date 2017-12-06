from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC
from web_admin import setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from campaign.models import terms_mapping
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
import logging


logger = logging.getLogger(__name__)

class AddMechanic(TemplateView, GetHeaderMixin):
    template_name = 'rule_configuration/add_mechanic.html'

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddMechanic, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== User go to Add Mechanic page ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding Mechanic ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        rule_id = context['rule_id']
        input_start_date = request.POST.get('dtp_start_date')
        input_end_date = request.POST.get('dtp_end_date')
        input_start_time = request.POST.get('dtp_start_time')
        input_end_time = request.POST.get('dtp_end_time')

        if input_start_date and input_end_date and input_start_time and input_end_time:
            start_hour = int(input_start_time[0:2])
            start_minute = int(input_start_time[-2:])
            end_hour = int(input_end_time[0:2])
            end_minute = int(input_end_time[-2:])
            start_date = datetime.strptime(input_start_date, "%Y-%m-%d")
            start_date = start_date.replace(hour=start_hour, minute=start_minute,
                                            second=0)
            end_date = datetime.strptime(input_end_date, "%Y-%m-%d")
            end_date = end_date.replace(hour=end_hour, minute=end_minute, second=0)

            param_start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            param_end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            param_start_date, param_end_date = '', ''
        params = {
            "event_name": request.POST.get('trigger'),
            "start_timestamp": param_start_date,
            "end_timestamp": param_end_date
        }

        success, status_code, message, data = RestFulClient.post(
            url=CREATE_MECHANIC.format(rule_id=rule_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params,
                                response=data, status_code=status_code)

        self.logger.info('========== Finish adding Mechanic ==========')
        return redirect('rule_configuration:add_condition', rule_id=rule_id, mechanic_id=data['id'])
