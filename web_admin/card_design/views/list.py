from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from django.shortcuts import render
import logging
from braces.views import GroupRequiredMixin
from authentications.apps import InvalidAccessToken
from web_admin.api_settings import SEARCH_CARD_PROVIDER, GET_ALL_CURRENCY_URL
from django.contrib import messages


logger = logging.getLogger(__name__)


class CardDesignList(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "card_design/list.html"
    group_required = "SYS_VIEW_LIST_CARD_DESIGN"
    url = api_settings.SEARCH_CARD_DESIGN
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardDesignList, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        currencies = self._get_currencies_list()
        providers = self._search_card_providers()
        card_type_list = self.get_card_types_list()
        context = {
            "currencies": currencies,
            "providers": providers,
            "card_type_list": card_type_list
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start get card design list ==========')
        # context = super(CardDesignList, self).get_context_data(**kwargs)
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

        self.logger.info('Params: {}'.format(params))

        is_success, status_code, status_message, data = RestFulClient.post(url=self.url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT,
                                                                           params=params)

        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        self.logger.info('Response_content_count: {}'.format(len(data)))
        
        is_permission_detail = check_permissions_by_user(self.request.user, 'SYS_VIEW_DETAIL_CARD_DESIGN')
        is_permission_edit = check_permissions_by_user(self.request.user, 'SYS_EDIT_CARD_DESIGN')

        for i in data:
            i['is_permission_detail'] = is_permission_detail
            i['is_permission_edit'] = is_permission_edit

        currencies = self._get_currencies_list()
        providers = self._search_card_providers()
        card_type_list = self.get_card_types_list()

        context = {'data': data,
            'card_design_name': card_design_name,
            'currency': currency,
            "currencies": currencies,
            "providers": providers,
            "card_type_list": card_type_list,
            }

        if card_type:
            context['card_type_id'] = int(card_type)
        if provider:
            context['provider'] = int(provider)
        if currency:
            context['currency'] = currency

        self.logger.info('========== Finish get card design list ==========')

        return render(request, self.template_name, context)

    def get_card_types_list(self):
        url = api_settings.CARD_TYPE_LIST
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = []
        else:
            data = []
            messages.add_message(
                self.request,
                messages.ERROR,
                "Something went wrong"
            )

        return data

    def _search_card_providers(self):
        is_success, status_code, status_message, data = RestFulClient.post(url=SEARCH_CARD_PROVIDER,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)
            else:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    status_message
                )
            data = []

        return data

    def _get_currencies_list(self):
        url = GET_ALL_CURRENCY_URL
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = []
            self.logger.info("Currency List is [{}]".format(len(data)))
        else:
            data = []

        if len(data) > 0:
            value = data.get('value', None)
            if value is not None:
                currency_list = [i.split('|') for i in value.split(',')]
                return currency_list
            else:
                return []
        else:
            return []
