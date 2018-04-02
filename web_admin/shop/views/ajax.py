

from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.http import JsonResponse

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
        id = kwargs['id']
        agent = get_agent_detail(self, id)
        return JsonResponse(agent)
