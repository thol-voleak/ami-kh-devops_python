import logging

from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from web_admin.api_settings import SEARCH_CARD_TYPE
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger


logger = logging.getLogger(__name__)


class ListView(GetHeaderMixin, TemplateView):
    template_name = "card_type/card_types_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Card Type List page ==========')
        data = self.get_card_types_list()
        result = {
            'card_type_list': data,
            'card_type_update_msg': self.request.session.pop('card_type_update_msg', None)
        }
        self.logger.info('========== Finished showing Card Type List page ==========')
        return result

    def get_card_types_list(self):
        self.logger.info('========== Start get Card Type List  ==========')
        is_success, status_code, status_message, data = RestFulClient.post(url=SEARCH_CARD_TYPE,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        API_Logger.post_logging(loggers=self.logger, response=data,
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get Card Type List  ==========')
        return data
