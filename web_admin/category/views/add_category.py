from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import api_settings
from authentications.apps import InvalidAccessToken
from django.shortcuts import render
from django.contrib import messages
from web_admin.api_logger import API_Logger
import logging


logger = logging.getLogger(__name__)


class AddCategory(TemplateView, GetHeaderMixin):

    template_name = "category/add_category.html"
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
        return super(AddCategory, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start create category ==========')

        context = super(AddCategory, self).get_context_data(**kwargs)
        is_category_enable = request.POST.get('category_status')
        category_name = request.POST.get('category_name')
        category_description = request.POST.get('category_description')
        category_image = request.POST.get('category_image')

        body = {
            "name": category_name,
            "description": category_description,
            "image_url": category_image
        }

        if is_category_enable:
            body['is_active']= True
        else:
            body['is_active']= False

        url = api_settings.ADD_CATEGORY
        success, status_code, status_message, data = RestFulClient.post(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=body)
        API_Logger.post_logging(loggers=self.logger, params=body, response=data, status_code=status_code)
        if success:
            self.logger.info('========== Finish create category ==========')
            messages.success(request, 'Added Successfully')
            return render(request, self.template_name)
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(status_message))
            raise InvalidAccessToken(status_message)
        else:
            return render(request, self.template_name)




