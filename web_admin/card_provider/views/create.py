from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from authentications.apps import InvalidAccessToken
from django.shortcuts import render, redirect
from django.contrib import messages
import logging


logger = logging.getLogger(__name__)


class CardProviderCreate(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "card_provider/create.html"
    logger = logger
    url = api_settings.CREATE_CARD_PROVIDER
    group_required = "SYS_ADD_PROVIDER"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardProviderCreate, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start create card provider ==========')
        provider_name = request.POST.get('provider_name')
        params = {}
        if not provider_name:
            return render(request, self.template_name)
        params['name'] = provider_name
        success, status_code, status_message, data = RestFulClient.post(url=self.url,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        timeout=settings.GLOBAL_TIMEOUT,
                                                                        params=params)
        self.logger.info('========== Finish create card provider ==========')
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Add provider successfully'
            )
            return redirect('card_provider:card_provider')
        else:
            if status_code in ['access_token_expire', 'authentication_fail',
                               'invalid_access_token', 'authentication_fail']:
                self.logger.info(
                    "{} for {} username".format(status_message, self.request.user))
                raise InvalidAccessToken(status_message)

            messages.add_message(
                request,
                messages.ERROR,
                status_message
            )
            return render(request, self.template_name)
