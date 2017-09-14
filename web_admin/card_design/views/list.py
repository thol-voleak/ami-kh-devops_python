from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from django.shortcuts import render
import logging
from authentications.apps import InvalidAccessToken


logger = logging.getLogger(__name__)


class CardDesignList(TemplateView, GetHeaderMixin):

    template_name = "card_design.html"
    group_required = "SYS_MANAGE_CARD DESIGN"
    url = api_settings.SEARCH_CARD_DESIGN
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardDesignList, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start get card design list ==========')
        context = super(CardDesignList, self).get_context_data(**kwargs)
        card_design_name = request.POST.get('card_design_name')
        card_type = request.POST.get('card_type')
        provider = request.POST.get('provider')
        currency = request.POST.get('currency')

        params = {}
        if card_design_name:
            params['name'] = card_design_name
        if card_type:
            params['card_type_id'] = int(card_type)
        if provider:
            params['provider'] = provider
        if currency:
            params['currency'] = currency

        is_success, status_code, status_message, data = RestFulClient.post(url=self.url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT,
                                                                           params=params)

        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        context.update({
            'data': data,
            'card_design_name': card_design_name,
            'card_type': card_type,
            'provider': provider,
            'currency': currency,
        })
        print(data)
        self.logger.info('========== Finish get card design list ==========')

        return render(request, self.template_name, context)
