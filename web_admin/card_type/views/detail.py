import logging

from django.shortcuts import render
from django.views.generic.base import TemplateView

from authentications.utils import get_correlation_id_from_username
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class CardTypeDetail(TemplateView, RESTfulMethods):
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
        self.logger.info('========== Start Get Card Type Detail ==========')
        api_path = api_settings.SEARCH_CARD_TYPE

        response_json, success = self._post_method(
            api_path=api_path,
            func_description="Search Card Type",
            logger=logger,
            params=params,
            only_return_data=False
        )
        self.logger.info("data={}".format(response_json.get('data')))
        try:
            card_type_detail = response_json.get('data')[0]
            timeout_create_card_in_second = int(card_type_detail['timeout_create_card']) / 1000
            timeout_get_card_detail_in_second = int(card_type_detail['timeout_get_card_detail']) / 1000
            card_type_detail.update({'timeout_create_card_in_second': '%g' % timeout_create_card_in_second,
                                     'timeout_get_card_detail_in_second': '%g' % timeout_get_card_detail_in_second})
        except IndexError:
            card_type_detail = {}
        self.logger.info('========== Finish Get Card Type Detail ==========')
        return card_type_detail
