from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from django.contrib import messages
from web_admin import api_settings, setup_logger
import logging
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin.api_settings import SEARCH_CARD_PROVIDER, GET_ALL_CURRENCY_URL
from web_admin.restful_client import RestFulClient
from django.conf import settings
from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class CreateView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "card_design/create.html"
    logger = logger

    group_required = "SYS_ADD_CARD_DESIGN"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

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
        self.logger.info('========== Start creating card design ==========')
        name = request.POST.get('name')
        pan_pattern = request.POST.get('pan_pattern')
        card_type_id = request.POST.get('card_type')
        currency = request.POST.get('currency')
        pre_sof_order_url = request.POST.get('pre_sof_order_url')
        pre_sof_order_read_timeout = request.POST.get('pre_sof_order_read_timeout')
        pre_link_url = request.POST.get('pre_link_url')
        pre_link_read_timeout = request.POST.get('pre_link_read_timeout')
        link_url = request.POST.get('link_url')
        link_read_timeout = request.POST.get('link_read_timeout')
        un_link_url = request.POST.get('un_link_url')
        un_link_read_timeout = request.POST.get('un_link_read_timeout')
        debit_url = request.POST.get('debit_url')
        debit_read_timeout = request.POST.get('debit_read_timeout')
        credit_url = request.POST.get('credit_url')
        credit_read_timeout = request.POST.get('credit_read_timeout')
        check_status_url = request.POST.get('check_status_url')
        check_status_read_timeout = request.POST.get('check_status_read_timeout')
        cancel_url = request.POST.get('cancel_url')
        cancel_read_timeout = request.POST.get('cancel_read_timeout')
        provider = request.POST.get('provider')


        body = {
            "name": name,
            "card_type_id": int(card_type_id),
            "is_active": True,
            "currency": currency,
            "pan_pattern": pan_pattern,
            "pre_sof_order_url": pre_sof_order_url,
            "pre_link_url": pre_link_url,
            "link_url": link_url,
            "un_link_url": un_link_url,
            "debit_url": debit_url,
            "credit_url": credit_url,
            "check_status_url": check_status_url,
            "cancel_url": cancel_url,
        }

        if pre_sof_order_read_timeout:
            body['pre_sof_order_read_timeout'] = int(pre_sof_order_read_timeout)
        if pre_link_read_timeout:
            body['pre_link_read_timeout'] = int(pre_link_read_timeout)
        if link_read_timeout:
            body['link_read_timeout'] = int(link_read_timeout)
        if un_link_read_timeout:
            body['un_link_read_timeout'] = int(un_link_read_timeout)
        if debit_read_timeout:
            body['debit_read_timeout'] = int(debit_read_timeout)
        if credit_read_timeout:
            body['credit_read_timeout'] = int(credit_read_timeout)
        if check_status_read_timeout:
            body['check_status_read_timeout'] = int(check_status_read_timeout)
        if cancel_read_timeout:
            body['cancel_read_timeout'] = int(cancel_read_timeout)

        url = api_settings.CREATE_CARD_DESIGN.format(provider_id=provider)
        self.logger.info('Params: {}'.format(body))
        success, data = self._create_card_design(url, body)

        self.logger.info('========== Finish creating card design ==========')

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Add Card Design successfully'
            )
            return redirect('card_design:card_designs')
        else:
            body['provider'] = int(provider)
            currencies = self._get_currencies_list()
            providers = self._search_card_providers()
            card_type_list = self.get_card_types_list()
            context = {
                "currencies": currencies,
                "providers": providers,
                "card_type_list": card_type_list,
                "body": body

            }

            return render(request, self.template_name, context)

    def _create_card_design(self, url, params):
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           loggers=self.logger, headers=self._get_headers(),
                                                                           params=params)
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
            data = {}

        return is_success, data

    def get_card_types_list(self):
        self.logger.info('========== Start get card type list ==========')
        url = api_settings.CARD_TYPE_LIST
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
            messages.add_message(
                self.request,
                messages.ERROR,
                "Something went wrong"
            )
        self.logger.info('Response_content_count: {}'.format(len(data)))
        self.logger.info('========== Finish get card type list ==========')
        return data

    def _search_card_providers(self):
        self.logger.info('========== Start get card provider list ==========')
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
        self.logger.info('Response_content_count: {}'.format(len(data)))
        self.logger.info('========== Finish get card provider list ==========')
        return data

    def _get_currencies_list(self):
        self.logger.info('========== Start get currency list ==========')
        url = GET_ALL_CURRENCY_URL
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = []
            self.logger.info("Currency List is [{}]".format(len(data)))
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        self.logger.info('========== Finish get currency list ==========')
        if len(data) > 0:
            value = data.get('value', None)
            if value is not None:
                currency_list = [i.split('|') for i in value.split(',')]
                return currency_list
            else:
                return []
        else:
            return []
