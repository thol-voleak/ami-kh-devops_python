import logging
from datetime import date
from web_admin.api_logger import API_Logger
from web_admin.api_settings import CREATE_FRAUD_TICKET
from web_admin import setup_logger, RestFulClient
from django.shortcuts import redirect, render
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)


class FPCreateView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = 'fraud_prevention/create.html'
    logger = logger

    group_required = "CREATE_FRAUD_TICKET"
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
        self.logger.info('========== Start creating Fraud Ticket ==========')

        data_type = request.POST.get('data_type')
        key_value = request.POST.get('key_value')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        context = super(FPCreateView, self).get_context_data(**kwargs)

        if not start_date:
            start_date = str(date.today())
        start_date += 'T00:00:01Z'

        if end_date:
            end_date += 'T23:59:59Z'
        else:
            end_date = None

        params = {
            "start_active_ticket_timestamp": start_date,
            "end_active_ticket_timestamp": end_date,
            "description": reason if reason != 'Others' else request.POST.get('notes'),
            "data": []
        }

        data_body = []
        ids = key_value.split(",")

        if data_type == 'virtual_card':
            params['action'] = 'unstop card'
            for i in ids:
                card_id = {'card_id' : int(i) if i.isnumeric() else i}
                data_body.append(card_id)
        elif data_type == 'device_id':
            params['action'] = 'register customer'
            for i in ids:
                device_id = {'device_id' : i}
                data_body.append(device_id)

        params['data'] = data_body
        self.logger.info(params)

        success, data, message = self.create_fraud_ticket(params)
        self.logger.info(data)
        self.logger.info(message)

        if success:
            result = {}
            result['success'] = []
            result['already_frozen'] = []
            result['not_exist'] = []
            card_or_device = 'card(s)' if data_type == 'virtual_card' else 'device(s)'
            summary_mes = ''

            for res in data['tickets']:
                level, result = self.extract_response(data_type, res, result)
                self.logger.info("mess")
                self.logger.info(result)

            if len(result['success']) > 0:
                summary_mes += '%d %s successfully frozen. ' % (len(result['success']), card_or_device)
            if len(result['already_frozen']) > 0:
                summary_mes += '%d %s is/are already frozen. ' % (len(result['already_frozen']), card_or_device)
            if len(result['not_exist']) > 0:
                summary_mes += '%d %s do(es) not exist.' % (len(result['not_exist']), card_or_device)

            context['summary_result'] = summary_mes
            context['result_messages'] = result
            context['is_success'] = True
        else:
            context['result_messages'] = message
            context['is_error'] = True

        self.logger.info(context['result_messages'])

        return render(request,self.template_name,context)

    def extract_response(self, data_type, res, result):
        object_type = 'Virtual Card' if data_type == 'virtual_card' else 'Device ID'
        id_field = 'card_id' if data_type == 'virtual_card' else 'device_id'

        if res['status'] != 'success':
            level = messages.ERROR
            if res['status'] == 'already frozen':
                result['already_frozen'].append( 'FAIL: %s #%s is already frozen' % (object_type, res[id_field]))
            elif res['status'] == 'does not exist':
                result['not_exist'].append('FAIL: %s #%s does not exist' % (object_type, res[id_field]))
        else:
            level = messages.SUCCESS
            result['success'].append('SUCCESS: Fraud ticket #%s successfully created for %s #%s' %(res['ticket_id'],object_type, res[id_field] ))
        return level, result

    def create_fraud_ticket(self, params):
        success, status_code, message, data = RestFulClient.post(
            url=CREATE_FRAUD_TICKET,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params,
                                response=data, status_code=status_code)

        return success, data, message
