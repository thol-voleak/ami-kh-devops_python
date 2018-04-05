

from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.http import JsonResponse
from web_admin import api_settings
from web_admin.restful_client import RestFulClient

import logging

from shop.utils import get_agent_detail


logger = logging.getLogger(__name__)


# def agent_detail(request, id):
#     agent = get_agent_detail(id)
#     return JsonResponse(agent)

class Agent_Detail(TemplateView, GetHeaderMixin):
    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(Agent_Detail, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start get agent detail ==========')
        api_path = api_settings.AGENT_DETAIL_PATH
        id = kwargs['id']
        params = {'id': id}
        success, status_code, status_message, data = RestFulClient.post(
                                                        url=api_path,
                                                        headers=self._get_headers(),
                                                        loggers=self.logger,
                                                        params=params
                                                        )
        self.logger.info("Params: {} ".format(params))
        if success:
            self.logger.info("{}".format(data))
            self.logger.info('========== Finish get agent detail ==========')
            if len(data['agents']) == 0:
                return JsonResponse({'wrong_agent': True})
            else:
                return JsonResponse(data['agents'][0])
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            return JsonResponse({"invalid_access_token":True})
        else:
            return JsonResponse({'wrong_agent': True})
