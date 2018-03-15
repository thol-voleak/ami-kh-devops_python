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
        self.logger.info('========== Start render category page ==========')
        context = super(CategoryList, self).get_context_data(**kwargs)
        categories = self.get_categories()
        list_category = categories[0].get('categories')

        ## Get all list category and list product for each category 
        if list_category is not None:
            for category in list_category:
                product_in_category = self.get_products(category['id'])
                category['product'] = product_in_category[0].get('products')
                category['product_count'] = len(category['product'])
            context['list_category'] = list_category
        #### TEST DATA ####
        # list_category = [{'id': 309, 'name': 'TC_EQP_04387_ulzhrndpevTC_EQP_04387_ulzhrndpevTC_EQP_04387_ulzhrndpev', 'description': 'description TC_EQP_04387_ulzhrndpev', 'image_url': 'http://fooimage/TC_EQP_04387_ulzhrndpev', 'is_active': True, 'is_deleted': True, 'created_timestamp': '2018-03-14T07:18:36Z', 'last_updated_timestamp': '2018-03-14T07:18:36Z', 'product': [], 'product_count': 0},
        #                 {'id': 22, 'name': 'TC_EQP_04387_ulzhrndpev', 'description': 'description TC_EQP_04387_ulzhrndpev', 'image_url': 'http://fooimage/TC_EQP_04387_ulzhrndpev', 'is_active': True, 'is_deleted': True, 'created_timestamp': '2018-03-14T07:18:36Z', 'last_updated_timestamp': '2018-03-14T07:18:36Z', 'product': [], 'product_count': 0},
        #                 ]
        # context['list_category'] = list_category
        ############################################################
        if categories[0].get('categories'):
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


