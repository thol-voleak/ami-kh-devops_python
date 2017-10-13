from braces.views import GroupRequiredMixin
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from django.contrib import messages
from web_admin.api_settings import AGENT_SMARTCARD_PATH, ADD_AGENT_SMART_CARD_PATH
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class SmartCardView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_AGENT_SMARTCARD"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/smart_card.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SmartCardView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting list agent smart card ==========')
        context = super(SmartCardView, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        agent_smartcard = self._get_agent_smartcard(agent_id)

        permissions = {
            'is_perm_add_smart_card': check_permissions_by_user(self.request.user, "CAN_ADD_AGENT_SMARTCARD"),
        }

        context = {
            "smartcards": agent_smartcard,
            'permissions': permissions,
        }
        self.logger.info('========== Finished getting agent smartcard ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not check_permissions_by_user(request.user, 'CAN_ADD_AGENT_SMARTCARD'):
            return render(request, 'web/permission-denied.html')

        self.logger.info('========== Start adding agent smart card ==========')
        context = super(SmartCardView, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        params = {
            "card_number": request.POST.get('number'),
            "card_serial": request.POST.get('serial')
        }
        is_success = self._add_agent_smart_card(agent_id, params)
        self.logger.info('========== Finished adding agent smartcard ==========')
        if is_success:
            return redirect(request.META['HTTP_REFERER'])
        else:
            agent_smartcard = self._get_agent_smartcard(agent_id)
            permissions = {
                'is_perm_add_smart_card': check_permissions_by_user(self.request.user, "CAN_ADD_AGENT_SMARTCARD"),
            }
            context = {
                "smartcards": agent_smartcard,
                'permissions': permissions,
            }
            return render(request, self.template_name, context)

    def _get_agent_smartcard(self, agent_id):
        params = {"agent_id": agent_id}
        is_success, status_code, status_message, data = RestFulClient.post(url=AGENT_SMARTCARD_PATH,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data

    def _add_agent_smart_card(self, agent_id, params):
        url = ADD_AGENT_SMART_CARD_PATH.format(agent_id)
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
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
                'Add agent smartcard successfully'
            )
        elif status_message == 'timeout':
            messages.add_message(
                self.request,
                messages.ERROR,
                "Can not add SmartCard for this user, please try again or contact technical support"
            )
        elif status_code == 'invalid_request':
            messages.add_message(
                self.request,
                messages.ERROR,
                "Invalid agent smartcard"
            )
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                "Got error and can't add new smartcard"
            )
        return is_success