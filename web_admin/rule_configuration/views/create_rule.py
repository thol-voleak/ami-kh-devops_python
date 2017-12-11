from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
from authentications.apps import InvalidAccessToken
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
import logging
from web_admin.api_logger import API_Logger
from datetime import datetime

logger = logging.getLogger(__name__)

class CreateRuleView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_CREATE_RULE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "rule_configuration/create_rule.html"
    path = api_settings.CREATE_RULE
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateRuleView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(CreateRuleView, self).get_context_data(**kwargs)
        context['start_date'] = datetime.now().strftime("%Y-%m-%d")
        #context['end_date'] = datetime.now().strftime("%Y-%m-%d")
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(CreateRuleView, self).get_context_data(**kwargs)
        self.logger.info('========== Start create rule ==========')
        name = request.POST.get('name')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        body ={
            'name':name,
            'start_date':start_date,
            'end_date':end_date,
            'start_time':start_time,
            'end_time':end_time,
            'description':description
        }
            
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date != '':
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                if end_time != '':
                    end_hour = int(end_time[0:2])
                    end_minute = int(end_time[-2:])
                    end_date_obj = end_date_obj.replace(hour=end_hour, minute=end_minute, second=0)
                end_date = end_date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
            if start_time != '':
                start_hour = int(start_time[0:2])
                start_minute = int(start_time[-2:])
                start_date_obj = start_date_obj.replace(hour=start_hour, minute=start_minute, second=0) 
            start_date = start_date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            body['error_msg'] = 'Date and time need to be in right format'
            body['border_color'] = "red"
            context.update(body)
            return render(request, self.template_name, context)

        params = {
            "name":name,
            "description":description,
            "start_active_timestamp":start_date,
            "is_active":True
        }
        if end_date != '':
            params['end_active_timestamp'] = end_date

        self.logger.info("param is : {}".format(params))

        success, status_code, status_message, data = RestFulClient.post(
            url=self.path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        #API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)
        self.logger.info('========== Finish create rule ==========')
        if success:
            return redirect('rule_configuration:add_mechanics', rule_id=data['id'])
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(status_message))
            raise InvalidAccessToken(status_message)
        elif status_message == 'Invalid date time':
            body['error_msg'] = 'End Date could not be less than Start Date'
            body['border_color'] = "red"
            context.update(body)
            return render(request, self.template_name,context )