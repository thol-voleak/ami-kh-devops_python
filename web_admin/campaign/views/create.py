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

class CreateCampaignView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_CREATE_CAMPAIGN"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "create.html"
    path = api_settings.CREATE_CAMPAIGN
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateCampaignView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(CreateCampaignView, self).get_context_data(**kwargs)
        context['start_date'] = datetime.now().strftime("%Y-%m-%d")
        context['end_date'] = datetime.now().strftime("%Y-%m-%d")
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(CreateCampaignView, self).get_context_data(**kwargs)
        self.logger.info('========== Start create campaign ==========')
        name = request.POST.get('name')
        description = request.POST.get('description')
        start_date = request.POST.get('dtp_from')
        end_date = request.POST.get('dtp_to')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        print("start date is ;{}".format(start_date))
        print("end date is ;{}".format(end_date))
        print("start time is ;{}".format(start_time))
        print("end time is ;{}".format(end_time))

        params = {
            "name":name,
            "description":description,
        }
        self.logger.info("param is : {}".format(params))

        success, status_code, message, data = RestFulClient.post(
            url=self.path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        # API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)
        self.logger.info('========== Finish create capmpaign ==========')
        if success:
            messages.success(request, 'The campaign is created successfully')
            return redirect('campaign:campaign')
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(message))
                raise InvalidAccessToken(message)

            context = {
                'name': name,
                'description': description
                #'start_time': start_time,
                #'end_time': end_time
            }

            if status_code.lower() in ["general_error"]:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Other error, please contact system administrator"
                )
            elif message == 'timeout':
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Request timed-out, please try again or contact system administrator"
                )
            else:
                messages.add_message (
                    request,
                    messages.ERROR,
                    message
                )

            return render(request, self.template_name, context) #