from authentications.utils import get_correlation_id_from_username
from web_admin.api_settings import SEARCH_CARD_TYPE
from web_admin.restful_methods import RESTfulMethods
from web_admin import setup_logger

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
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
        data, success = self._post_method(api_path=SEARCH_CARD_TYPE,
                                         func_description="Card Type List",
                                         logger=logger)
        return data
