from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from django.shortcuts import render
import logging


logger = logging.getLogger(__name__)


class CardDesignList(TemplateView, GetHeaderMixin):

    template_name = "card_design.html"
    url = "api-gateway/report/"+api_settings.API_VERSION+"/cards/sofs"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardDesignList, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start get card design list ==========')
        context = super(CardDesignList, self).get_context_data(**kwargs)
        data = self.get_card_design()
        context['data'] = data

        return render(request, self.template_name, context)

    def get_card_design(self):
        is_success, status_code, status_message, data = RestFulClient.post(url=self.url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        return data
