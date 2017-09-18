from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.views.generic.base import TemplateView
from web_admin.api_settings import GET_DETAIL_PROVIDER, UPDATE_CARED_PROVIDER
from authentications.apps import InvalidAccessToken
import logging

logger = logging.getLogger(__name__)


class UpdateView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "SYS_VIEW_DETAIL_PROVIDER"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "card_provider/update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start update provider detail ==========')
        context = super(UpdateView, self).get_context_data(**kwargs)

        provider_id = context['provider_id']

        url = GET_DETAIL_PROVIDER.format(provider_id=provider_id)

        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        self.logger.info('Response_content: {}'.format(data))
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
        context['data'] = data
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        provider_id = context['provider_id']

        url  = UPDATE_CARED_PROVIDER.format(provider_id=provider_id)

        provider_name = request.POST.get('provider_name')

        params = {
            'name': provider_name
        }

        self.logger.info('Params: {}'.format(params))

        is_success, status_code, status_message, data = RestFulClient.put(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           timeout=settings.GLOBAL_TIMEOUT,
                                                                           params=params)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        self.logger.info('========== Finish update provider detail ==========')

        data = {'id': provider_id, 'name': provider_name}
        context.update({
            'data': data,
            'msg': 'Update provider successfully'
        })
        return render(request, self.template_name, context)
