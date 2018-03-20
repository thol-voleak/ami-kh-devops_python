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


class CategoryList(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    group_required = "CAN_MANAGE_CATEGORY"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "category/list.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CategoryList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)

        permissions = {}
        permissions['CAN_ADD_CATEGORY'] = self.check_membership(["CAN_ADD_CATEGORY"])
        permissions['CAN_EDIT_CATEGORY'] = self.check_membership(["CAN_EDIT_CATEGORY"])
        permissions['CAN_DELETE_CATEGORY'] = self.check_membership(["CAN_DELETE_CATEGORY"])
        self.logger.info('========== Start render category page ==========')

        context.update({
            'permissions': permissions
        })
        categories = self.get_categories()

        list_category = categories[0].get('categories')

        all_list_product = self.get_all_list_products() 
        all_list_product = all_list_product[0].get('products')

        # Get all list category and list product for each category
        if list_category:
            for category_unit in list_category[::]:
                if category_unit['is_deleted']:
                    list_category.remove(category_unit)
                    continue
                product_list = []
                for product_unit in all_list_product:
                    if all_list_product: 
                        if not product_unit['is_deleted'] and product_unit['category_id'] == category_unit['id']:
                            product_list.append(product_unit)
                category_unit['product'] = product_list

            context['list_category'] = list_category

            # get default category to view
            default_category = categories[0].get('categories')[0]
            category_id = default_category['id']
            if category_id:
                category_detail = self.get_category_detail(category_id)
                products_default = self.get_products(category_id)

                context.update({
                    'category_detail': category_detail[0]['categories'][0],
                    'products': products_default[0].get('products'),
                })
        self.logger.info('========== Finish render category page ==========')
        return render(request, self.template_name, context)

    def get_categories(self):
        self.logger.info('========== Start get category list ==========')
        api_path = api_settings.GET_CATEGORIES

        body = {
            "paging": False
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body,
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get category list ==========')

        return data, success, status_message

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
        API_Logger.post_logging(loggers=self.logger, params=body,
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get category detail ==========')

        return data, success, status_message

    def get_products(self, category_id):
        self.logger.info('========== Start get list product ==========')
        api_path = api_settings.GET_PRODUCTS

        body = {
            "category_id": category_id,
            "paging": False
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body,
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get list product ==========')

        return data, success, status_message

    def get_all_list_products(self):
        self.logger.info('========== Start get list product ==========')
        api_path = api_settings.GET_PRODUCTS

        body = {
            "paging": False
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body,
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get list product ==========')

        return data, success, status_message


