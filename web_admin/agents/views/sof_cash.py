from braces.views import GroupRequiredMixin

from authentications.apps import InvalidAccessToken
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from django.contrib import messages
from web_admin.api_settings import GET_REPORT_AGENT_BALANCE
from web_admin.api_settings import GET_ALL_CURRENCY_URL
from web_admin.api_settings import CREATE_AGENT_BALANCE_URL
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class SOFCashView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_VIEW_AGENT_SOFCASH"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/agent_sof_cash_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SOFCashView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting list agent sof cash ==========')
        context = super(SOFCashView, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        agent_sof_cash = self._get_agent_sof_cash(agent_id)
        currencies, success = self._get_currency_choices()
        self.logger.info('currencies: {}'.format(currencies))

        permissions = {
            'is_permission_add_sofcash': check_permissions_by_user(self.request.user, "CAN_ADD_AGENT_SOFCASH"),
        }
        context = {
            "data": agent_sof_cash,
            'agent_id': agent_id,
            'currencies': currencies,
            'permissions': permissions
        }
        self.logger.info('========== Finished getting agent sof cash ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not check_permissions_by_user(request.user, 'CAN_ADD_AGENT_SOFCASH'):
            return render(request, 'web/permission-denied.html')

        self.logger.info('========== Start adding agent sof cash ==========')
        context = super(SOFCashView, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        params = {
            "currency": request.POST.get('currency_id'),
            "user_id": agent_id,
            "user_type_id": 2,
        }
        self._add_agent_sof_cash(params)
        self.logger.info('========== Finished adding agent sof cash ==========')

        return redirect('agents:agent-sofcash', agent_id=agent_id)

    def _get_agent_sof_cash(self, agent_id):
        params = {"user_id": agent_id}
        is_success, status_code, status_message, data = RestFulClient.post(url=GET_REPORT_AGENT_BALANCE, params=params, loggers=self.logger, headers=self._get_headers(), timeout=settings.GLOBAL_TIMEOUT)
        API_Logger.post_logging(loggers=self.logger, params=params, response=data["cash_sofs"] if is_success else data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data

    def _get_currency_choices(self):
        self.logger.info('========== Start Getting Currency Choices ==========')
        url = GET_ALL_CURRENCY_URL
        is_success, status_code, data = RestFulClient.get(url, loggers=self.logger, headers=self._get_headers(), timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, response=data,
                                status_code=status_code, is_getting_list=True)

        if is_success:
            value = data.get('value', '')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = [], False
        self.logger.info('========== Finish Getting Currency Choices ==========')
        return result

    def _add_agent_sof_cash(self, params):
        is_success, status_code, status_message, data = RestFulClient.post(url=CREATE_AGENT_BALANCE_URL,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)

        if is_success:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                'New currency added as cash SOF'
            )
        elif status_message == 'timeout':
            messages.add_message(
                self.request,
                messages.ERROR,
                "Transaction Timeout : Cannot add SOF Cash, please try again or contact technical support"
            )
        elif status_message == 'Invalid SOF information' and status_code == 'invalid_request':
            messages.add_message(
                self.request,
                messages.ERROR,
                "Cannot add SOF Cash - '" + status_message + "'"
            )
        else :
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
        return is_success