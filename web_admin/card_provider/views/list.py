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


class CardProviderList(TemplateView, GetHeaderMixin):

    template_name = "card_provider/card_provider.html"
    url = api_settings.SEARCH_CARD_PROVIDER
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardProviderList, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start get card provider list ==========')
        context = super(CardProviderList, self).get_context_data(**kwargs)
        provider_name = request.POST.get('provider_name')
        params = {}
        if provider_name:
            params['name'] = provider_name
        self.logger.info('Params: {}'.format(params))
        is_success, status_code, status_message, data = RestFulClient.post(url=self.url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT,
                                                                           params=params)
        self.logger.info('Response_content_count: {}'.format(len(data)))
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        is_permission_detail = check_permissions_by_user(self.request.user, 'SYS_VIEW_DETAIL_PROVIDER')
        is_permission_edit = check_permissions_by_user(self.request.user, 'SYS_EDIT_PROVIDER')

        for i in data:
            i['is_permission_detail'] = is_permission_detail
            i['is_permission_edit'] = is_permission_edit

        context.update({
            'data': data,
            'provider_name': provider_name
        })
        self.logger.info('========== Finish get card provider list ==========')

        return render(request, self.template_name, context)

