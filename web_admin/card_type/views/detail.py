import logging

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_correlation_id_from_username
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.api_logger import API_Logger


logger = logging.getLogger(__name__)


class CardTypeDetail(GetHeaderMixin, TemplateView):
    template_name = "card_type/card_type_detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardTypeDetail, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(CardTypeDetail, self).get_context_data(**kwargs)
        self.logger.info('========== Start showing Card Type Detail page ==========')
        card_type_id = context['card_type_id']

        params = {'id': card_type_id}

        data = self._get_card_type_detail(params)

        context = {
            'card_type_info': data,
            'card_type_update_msg': self.request.session.pop('card_type_update_msg', None)
        }

        self.logger.info('========== Finished showing Card Type Detail page ==========')

        return render(request, self.template_name, context)

    def _get_card_type_detail(self, params):
        api_path = api_settings.SEARCH_CARD_TYPE

        is_success, status_code, status_message, data = RestFulClient.post(url= api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)

        try:
            card_type_detail = data[0]
            timeout_create_card_in_second = int(card_type_detail['timeout_create_card']) / 1000
            timeout_get_card_detail_in_second = int(card_type_detail['timeout_get_card_detail']) / 1000
            card_type_detail.update({'timeout_create_card_in_second': '%g' % timeout_create_card_in_second,
                                     'timeout_get_card_detail_in_second': '%g' % timeout_get_card_detail_in_second})
        except IndexError:
            card_type_detail = {}
        timeout_update_card_status_in_second = ''
        if card_type_detail:
            try:
                result = int(card_type_detail['timeout_update_card_status']) / 1000
            except Exception as e:
                timeout_update_card_status_in_second = ''
            else:
                timeout_update_card_status_in_second = result
        if card_type_detail['timeout_update_card_status'] is not None:
            card_type_detail.update({'timeout_update_card_status': '%g' % timeout_update_card_status_in_second})
        
        return card_type_detail
