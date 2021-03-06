from braces.views import GroupRequiredMixin

from authentications.apps import InvalidAccessToken
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.utils import encrypt_text_agent, setup_logger
from django.contrib import messages
from web_admin.api_settings import AGENT_ADD_IDENTITY_PATH
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from agents.utils import get_all_agent_identity_types
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AddAgentIdentities(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_ADD_AGENT_IDENTITIES"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/add_agent_identities.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddAgentIdentities, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== User go to Add Agent Identity page ==========')
        context = super(AddAgentIdentities, self).get_context_data(**kwargs)
        agent_id = kwargs.get('agent_id')
        context['agent_id'] = agent_id
        context['params'] = {}
        list_identity_type = get_all_agent_identity_types(self)
        context['list_identity_type'] = list_identity_type
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        context = super(AddAgentIdentities, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        self.logger.info('========== Start adding agent identity ==========')
        username = request.POST.get('user_name')
        params = {'username': username}
        manual_password = request.POST.get('manual_password')
        identity_type_id = int(request.POST.get('identity_type_id'))

        list_identity_type = get_all_agent_identity_types(self)
        context['list_identity_type'] = list_identity_type

        params['identity_type_id'] = identity_type_id
        if manual_password:
            params['password'] = encrypt_text_agent(manual_password)
        else:
            params['password'] = ''
            params['auto_generate_password'] = True

        success, message = self._add_agent_identity(agent_id, params)

        self.logger.info('========== Finish adding agent identity ==========')

        if success:
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Agent Identity created successfully')
            return redirect('agents:agent_identities', agent_id=agent_id)

        elif message == 'timeout':
            messages.add_message(request, messages.ERROR,
                                 'Transaction Timeout : Cannot add identities, please try again or contact technical support')
            params['password'] = manual_password
            params['identity_type_id'] = identity_type_id
            context['agent_id'] = agent_id
            context['params'] = params
            return render(request, self.template_name, context=context)
        else:
            msg = "Cannot add identities for agent - " + message
            messages.add_message(request,
                                 messages.ERROR,
                                 msg)
            params['password'] = manual_password
            params['identity_type_id'] = identity_type_id
            context['agent_id'] = agent_id
            context['params'] = params
            return render(request, self.template_name, context=context)

    def _add_agent_identity(self, agent_id, body):
        url = AGENT_ADD_IDENTITY_PATH.format(agent_id=agent_id)
        # url = 'http://localhost:4892/timeout'
        success, status_code, message, data = RestFulClient.post(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=body
        )

        API_Logger.post_logging(loggers=self.logger,
                                params=body,
                                response=data,
                                status_code=status_code)
        return success, message
