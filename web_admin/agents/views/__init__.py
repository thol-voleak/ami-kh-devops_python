import json

from braces.views import GroupRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView

from authentications.utils import check_permissions_by_user, get_correlation_id_from_username
from web_admin import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.api_settings import AGENT_DETAIL_PATH
from web_admin.restful_methods import RESTfulMethods
from web_admin import api_settings, setup_logger

import logging

logger = logging.getLogger(__name__)


class AgentAPIService(RESTfulMethods):
    def get_agent_profile(self, agent_id):
        body = {'id': agent_id}
        data, success = self._post_method(api_path=api_settings.AGENT_DETAIL_PATH,
                                          func_description="Agent detail",
                                          logger=logger, params=body)
        data = data.get('agents', [])
        return data[0]

    def get_agent_types(self, agent_id):
        # body = {'id': agent_id}
        data, success = self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                          func_description="Agent Type List",
                                          logger=logger)
        newdata = [i for i in data if not i['is_deleted']]
        return newdata, success

    def get_agent_detail(self, agent_id):
        body = {'id': agent_id}
        data, success = self._post_method(api_path=api_settings.AGENT_DETAIL_PATH,
                                          func_description="Agent detail",
                                          logger=logger, params=body)
        data = data.get('agents', [])
        context = {
            'agent': data[0],
            'agent_id': agent_id,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }
        return context, success

    def get_agent_identity(self, agent_id):
        body = {'agent_id': agent_id}
        data, success = self._post_method(api_path=api_settings.GET_AGENT_IDENTITY_URL.format(agent_id=agent_id),
                                          func_description="Get agent identity",
                                          logger=logger,
                                          params=body)
        context = {
            'agent_identities': data
        }
        return context, success

    def get_agent_classification(self, agent_classification_id):
        body = {'id': agent_classification_id}
        data, success = self._post_method(api_path=api_settings.GET_AGENT_CLASSIFICATION_URL,
                                          func_description="Get agent classification",
                                          logger=logger,
                                          params=body)
        context = {
            'agent_classifications': data['classifications']
        }
        return context, success

    def get_mm_card_type(self, mm_card_type_id):
        body = {'id': mm_card_type_id}
        data, success = self._post_method(api_path=api_settings.GET_MM_CARD_TYPES,
                                          func_description="Get agent mm card type",
                                          logger=logger,
                                          params=body)
        context = {
            'mm_card_type': data
        }
        return context, success

    def get_mm_card_type_level(self, mm_card_type_level_id):
        body = {'id': mm_card_type_level_id}
        data, success = self._post_method(api_path=api_settings.GET_MM_CARD_TYPE_LEVELS,
                                          func_description="Get agent mm card type levels",
                                          logger=logger,
                                          params=body)
        context = {
            'mm_card_type_level': data
        }
        return context, success

    def get_accreditation_status(self, accreditation_status_id):
        body = {'id': accreditation_status_id}
        data, success = self._post_method(api_path=api_settings.GET_ACCREDITATION_STATUS,
                                          func_description="Get agent accreditation status",
                                          logger=logger,
                                          params=body)
        context = {
            'accreditation_status': data
        }
        return context, success

    def get_currencies(self, agent_id):
        url = api_settings.GET_REPORT_AGENT_BALANCE
        body = {
            'user_id': agent_id,
            'user_type': 2,
            "paging": False,
            "page_index": -1,
        }
        data, success = self._post_method(api_path=url,
                                          func_description="currency list by agent",
                                          logger=logger,
                                          params=body)
        currencies_str = ''
        data = data['cash_sofs']
        if success and len(data) > 0:
            currencies_str = ', '.join([elem["currency"] for elem in data])

        return currencies_str, success

    def get_agent_type_name(self, agent_type_id):
        agent_types_list, success = self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                                      func_description="Agent Type List",
                                                      logger=logger)
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


class AgentDetailService(GroupRequiredMixin, RESTfulMethods, TemplateView):
    group_required = "CAN_VIEW_AGENT"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger
    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentDetailService, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def post(self, request):
        agent_id = self.request.POST.get('agent_id', None);

        body = {'id': agent_id}
        success, status_code, status_message, data = RestFulClient.post(url=AGENT_DETAIL_PATH, headers=self._get_headers(),
                                                                        params=body, loggers=self.logger)
        API_Logger.post_logging(
            loggers=self.logger,
            params=body,
            response=data.get('agents', []),
            status_code=status_code,
            is_getting_list=True
        )
        if success:
            data = data.get('agents', [])
            data = data[0] if len(data) > 0 else None
        else:
            data = {}
        return HttpResponse(json.dumps({"data": data}))
