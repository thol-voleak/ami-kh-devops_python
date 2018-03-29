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
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class CategoryData(TemplateView, GetHeaderMixin):

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CategoryData, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start get category data ==========')
        category_id = request.POST.get("categoryId")
        category_detail, success, message, status_code = self.get_category_detail(category_id)
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            return JsonResponse({"status": "1"})
        if success:
            product_list, success, message = self.get_products(category_id)
            active_product = []
            for product in product_list.get('products'):
                if not product['is_deleted']:
                    active_product.append(product)
            self.logger.info('========== Finish get category data ==========')
            return JsonResponse({"status":"2", "category_detail":category_detail, "product_list": active_product})


    def get_category_detail(self, category_id):
        self.logger.info('========== Start get category detail ==========')
        api_path = api_settings.GET_CATEGORIES

        body = {
            "id": category_id
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        data = data or {}
        if status_code not in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            API_Logger.post_logging(loggers=self.logger, params=body,
                                    status_code=status_code, is_getting_list=False, response=data)

        self.logger.info('========== Finish get category detail ==========')
        return data, success, status_message, status_code

    def get_products(self, category_id):
        self.logger.info('========== Start get list product ==========')
        api_path = api_settings.GET_PRODUCTS

        body = {
            "product_category_id": category_id,
            "paging": False,
            "is_deleted": False
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT,)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body,
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get list product ==========')

        return data, success, status_message
