from braces.views import GroupRequiredMixin

from agents.views import AgentAPIService

from web_admin.api_logger import API_Logger
from web_admin.restful_client import RestFulClient
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentDelete(GroupRequiredMixin, TemplateView, AgentAPIService):
    group_required = "CAN_DELETE_AGENT"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agents/delete.html"
    get_agent_identity_url = api_settings.GET_AGENT_IDENTITY_URL
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentDelete, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start Deleting Agent ==========')
        context = super(AgentDelete, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        api_path = api_settings.AGENT_DELETE_URL.format(agent_id=agent_id)

        success, status_code, status_message = RestFulClient.delete(
            url=api_path,
            headers=self._get_headers(),
            loggers=self.logger)

        API_Logger.delete_logging(loggers=self.logger,
                                  status_code=status_code)

        self.logger.info('========== Finish Deleting Agent ==========')
        if success:
            request.session['agent_delete_msg'] = 'Deleted data successfully'
            previous_page = request.POST.get('previous_page')
            if previous_page:
                # Forward update case to detail after execute delete action.
                if "update" in previous_page:
                    previous_page = previous_page.replace('update/', '', 1)
                return HttpResponseRedirect(previous_page)
        else:
            request.session['agent_message'] = 'Delete agent fail. Please try again or contact support.'
            request.session['agent_redirect_from_delete'] = True
        return redirect('agents:agent-list')



    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Delete Agent page ==========')
        context = super(AgentDelete, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        context, status = self.get_agent_detail(agent_id)
        agent_identity, status_get_agent_identity = self.get_agent_identity(agent_id)

        currencies, status_get_currency = self.get_currencies(agent_id)
        if status and status_get_agent_identity and status_get_currency:
            agent_type_name, status = self.get_agent_type_name(context['agent']['agent_type_id'])
            if status:
                if len(agent_identity['agent_identities']) > 0:
                    context.update({
                        'status_get_agent_identity': agent_identity['agent_identities'][0],
                    })

                context.update({
                    'agent_type_name': agent_type_name,
                    'currencies': currencies
                })
            else:
                context.update({
                    'agent_type_name': context.agent.agent_type_id
                })
            if context['agent']['mm_card_type_id']:
                mm_card_type_data, status = self.get_mm_card_type(
                    context['agent']['mm_card_type_id'])
                if status:
                    context.update({
                        'mm_card_type_name': mm_card_type_data['mm_card_type'][0]['name']
                    })
                else:
                    context.update({
                        'mm_card_type_name': context['agent']['mm_card_type_id']
                    })

            if context['agent']['mm_card_level_id']:
                mm_card_type_level, status = self.get_mm_card_type_level(
                    context['agent']['mm_card_level_id'])
                if status:
                    context.update({
                        'mm_card_type_level_name': mm_card_type_level['mm_card_type_level'][0]['level']
                    })
                else:
                    context.update({
                        'mm_card_type_level_name': context['agent']['mm_card_level_id']
                    })
            if context['agent']['accreditation']['status_id']:
                accreditation_status, status = self.get_accreditation_status(
                    context['agent']['accreditation']['status_id'])
                if status:
                    context.update({
                        'accreditation_status_name': accreditation_status['accreditation_status'][0]['status']
                    })
                else:
                    context.update({
                        'accreditation_status_name': context['agent']['accreditation']['status_id']
                    })
            if context['agent']['agent_classification_id']:
                agent_classification_data, status = self.get_agent_classification(context['agent']['agent_classification_id'])
                if status:
                    context.update({
                        'agent_classification_name': agent_classification_data['agent_classifications'][0]['name']
                    })
                else:
                    context.update({
                        'agent_classification_name': context.agent.agent_classification_id
                    })
            if context['agent']['referrer_user_type_id']:
                referrer_agent_type_name, status = self.get_agent_type_name(context['agent']['referrer_user_type_id'])
                if status:
                    context.update({
                        'referrer_agent_type_name': referrer_agent_type_name
                    })
                else:
                    context.update({
                        'referrer_agent_type_name': context.agent.referrer_user_type_id
                    })
        else:
            context = {'agent': {}}

        self.logger.info('========== Finished showing Delete Agent page ==========')
        return context
