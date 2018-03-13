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
from web_admin.api_logger import API_Logger
import logging


logger = logging.getLogger(__name__)


class CategoryList(TemplateView, GetHeaderMixin):

    template_name = "category/list.html"
    logger = logger
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CategoryList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        categories = self.get_category()
        print(categories)
        return render(request, self.template_name)

    # def post(self, request, *args, **kwargs):
    #     self.logger.info('========== Start create category ==========')

    def get_category(self):
        api_path = api_settings.GET_CATEGORY

        body = {
            "paging": False
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('cards', []),
                                status_code=status_code, is_getting_list=True)

        return data, success, status_message


