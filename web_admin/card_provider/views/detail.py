from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import render
from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.api_settings import GET_DETAIL_PROVIDER
from authentications.apps import InvalidAccessToken
import logging

logger = logging.getLogger(__name__)


class DetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "SYS_VIEW_DETAIL_PROVIDER"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "card_provider/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting provider detail ==========')
        context = super(DetailView, self).get_context_data(**kwargs)

        provider_id = context['provider_id']

        url = GET_DETAIL_PROVIDER.format(provider_id=provider_id)

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
        is_permission_edit = check_permissions_by_user(self.request.user, 'SYS_EDIT_PROVIDER')
        context['is_permission_edit'] = is_permission_edit
        context['data'] = data

        self.logger.info('========== Finish getting provider detail ==========')
        return render(request, self.template_name, context)
