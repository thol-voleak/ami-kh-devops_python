from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
from authentications.apps import InvalidAccessToken
import logging

logger = logging.getLogger(__name__)

class DetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "card_design/detail.html"
    logger=logger

    group_required = "SYS_VIEW_DETAIL_CARD_DESIGN"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))

        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        card_id = context['card_id']
        provider_id = context['provider_id']
        return self._get_card_design_detail(provider_id, card_id)

    def _get_card_design_detail(self, provider_id, card_id):
        self.logger.info('========== Start get card design detail ==========')
        is_permission_edit = check_permissions_by_user(self.request.user, 'SYS_EDIT_CARD_DESIGN')
        url = api_settings.CARD_DESIGN_DETAIL.format(provider_id=provider_id, card_id=card_id)
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = {}
            self.logger.info("Card design detail is [{}]".format(data))
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            else:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    "Something went wrong"
                )
            data = {}
        self.logger.info('========== Finish get card design detail ==========')
        return {"body": data,
                "is_permission_edit": is_permission_edit}


