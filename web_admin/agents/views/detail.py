from braces.views import GroupRequiredMixin

from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from agents.views import AgentAPIService

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class DetailView(GroupRequiredMixin, TemplateView, AgentAPIService):
    group_required = "CAN_VIEW_AGENT"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agents/detail.html"
    get_agent_identity_url = api_settings.GET_AGENT_IDENTITY_URL
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Agent Detail page ==========')
        try:
            context = super(DetailView, self).get_context_data(**kwargs)
            agent_id = context['agent_id']

            context, status = self._get_agent_detail(agent_id)
            agent_identity, status_get_agent_identity = self._get_agent_identity(agent_id)
            currencies, status_get_currency = self._get_currencies(agent_id)

            context['msgs'].update({'agent_update_msg': self.request.session.pop('agent_update_msg', None)})

            if status and status_get_agent_identity and status_get_currency:

                agent_type_id = context['agent']['agent_type_id'] if context['agent'][
                                                                         'agent_type_id'] is not None else 0
                agent_type_name, status = self._get_agent_type_name(agent_type_id)

                if status and status_get_agent_identity and status_get_currency:
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
                    agent_classification_data, status = self.get_agent_classification(
                        context['agent']['agent_classification_id'])
                    if status:
                        context.update({
                            'agent_classification_name': agent_classification_data['agent_classifications'][0]['name']
                        })
                    else:
                        context.update({
                            'agent_classification_name': context.agent.agent_classification_id
                        })
                if context['agent']['referrer_user_type_id']:
                    referrer_agent_type_name, status = self.get_agent_type_name(
                        context['agent']['referrer_user_type_id'])
                    if status:
                        context.update({
                            'referrer_agent_type_name': referrer_agent_type_name
                        })
                    else:
                        context.update({
                            'referrer_agent_type_name': context.agent.referrer_user_type_id
                        })
        except Exception as ex:
            logging.error(ex)
            context = {'agent': {}}
        self.logger.info('========== Finished showing Agent Detail page ==========')
        return context

    def _get_currencies(self, agent_id):
        self.logger.info("================== Start getting currency ==================")
        params = {
            'user_id': agent_id,
            'user_type': 2,
            "paging": False,
            "page_index": -1
        }
        data, success = self._post_method(api_path=api_settings.GET_REPORT_AGENT_BALANCE, params=params)
        self.logger.info("================== Finish getting currency ==================")
        currencies_str = ''
        data = data['cash_sofs']
        if success and data:
            currencies_str = ', '.join([elem["currency"] for elem in data])

        return currencies_str, success

    def _get_agent_detail(self, agent_id):
        body = {'id': agent_id}
        data, success = self._post_method(api_path=api_settings.AGENT_DETAIL_PATH,
                                          func_description="Agent detail",
                                          logger=logger, params=body)
        agents_list = data.get('agents', [])

        context = {
            'agent': agents_list[0],
            'agent_id': agent_id,
            'msgs': {
                'get_msg': self.request.session.pop('agent_registration_msg', None),
                'del_msg': self.request.session.pop('agent_delete_msg', None)
            }
        }
        return context, success

    def _get_agent_identity(self, agent_id):
        self.logger.info("================== Start getting agent identity  ================== ")

        params = {"agent_id": agent_id}
        data, success = self._post_method(api_path=self.get_agent_identity_url, func_description=None, logger=self.logger, params=params, only_return_data=True)

        context = {
            'agent_identities': data
        }
        self.logger.info("================== Finish getting agent identity [{}] agent Id ================== ")
        return context, success

    def _get_agent_type_name(self, agent_type_id):
        self.logger.info("================== Start getting agent type list ==================")
        agent_types_list, success = self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                                      func_description="Agent Type List",
                                                      logger=logger)
        self.logger.info("================== Finish getting agent type list ==================")

        if success:
            my_id = int(agent_type_id)
            for x in agent_types_list:
                if x['id'] == my_id:
                    agent_type_name = x['name']
                    return agent_type_name, True
            data = 'Unknown', True
        else:
            data = None, False

        return data
