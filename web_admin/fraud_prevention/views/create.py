import logging
from datetime import date
from web_admin.api_logger import API_Logger
from braces.views import GroupRequiredMixin
from web_admin.api_settings import CREATE_FRAUD_TICKET
from web_admin import setup_logger, RestFulClient
from django.shortcuts import redirect, render
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user


logger = logging.getLogger(__name__)


class FPCreateView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = 'fraud_prevention/create.html'
    logger = logger

    group_required = "CAN_VIEW_CLIENTS"
    login_url = 'web:permission_denied'
    raise_exception = False
    path = CREATE_FRAUD_TICKET

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(FPCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== User go to Create Fraud Ticket page ==========')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        self.logger.info( '========== Start creating Fraud Ticket ==========')

        data_type = request.POST.get('data_type')
        key_value = request.POST.get('key_value')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        if not start_date:
            start_date = str(date.today())
        start_date += 'T00:00:01Z'

        if end_date:
            end_date += 'T23:59:59Z'

        params = {
            "start_active_ticket_timestamp": start_date,
            "end_active_ticket_timestamp": end_date,
            "description": reason if reason != 'Others' else request.POST.get('notes'),
            "data": {}
        }

        if data_type == 'virtual_card':
            params['action'] = 'unstop card'
            params['data']['card_id'] = int(key_value) if key_value.isnumeric() else key_value
        elif data_type == 'device_id':
            params['action'] = 'register_customer'
            params['data']['device_id'] = key_value

        success, data, message = self.create_fraud_ticket(params)
        self.logger.info('========== Finish creating Fraud Ticket ==========')

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Fraud Ticket #{} is created'.format(data.get('ticket_id')))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message)
        return redirect("fraud_prevention:fraud_prevention")

    def create_fraud_ticket(self, params):
        success, status_code, message, data = RestFulClient.post(
            url=CREATE_FRAUD_TICKET,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params,
                                response=data, status_code=status_code)

        return success, data, message