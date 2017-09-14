from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from django.shortcuts import render
import logging


logger = logging.getLogger(__name__)


class CardProviderList(TemplateView, GetHeaderMixin):

    template_name = "card_provider.html"
    url = "api-gateway/report/"+api_settings.API_VERSION+"/cards/sofs/providers"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardProviderList, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start get card provider list ==========')
        context = super(CardProviderList, self).get_context_data(**kwargs)
        provider_name = request.POST.get('provider_name')
        params = {}
        if provider_name:
            params['name'] = provider_name
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
            'provider_name': provider_name
        })
        self.logger.info('========== Finish get card provider list ==========')

        return render(request, self.template_name, context)

