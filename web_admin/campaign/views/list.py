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
from web_admin.api_settings import GET_CAMPAIGNS
from django.contrib import messages


logger = logging.getLogger(__name__)


class CamPaignList(TemplateView, GetHeaderMixin):

    template_name = "list.html"
    group_required = "SYS_VIEW_LIST_CARD_DESIGN"
    url = api_settings.SEARCH_CARD_DESIGN
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CamPaignList, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        data = self.get_campaigns()
        print(data)
        context = {
            'data': data
        }
        return render(request, self.template_name, context)

    def get_campaigns(self):
        url = GET_CAMPAIGNS
        self.logger.info('========== Start get campaigns list ==========')
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        self.logger.info('========== Finish get campaigns list ==========')
        return data[::-1]