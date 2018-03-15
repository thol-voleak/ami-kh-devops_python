from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import api_settings
from authentications.apps import InvalidAccessToken
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from web_admin.api_logger import API_Logger
import logging


logger = logging.getLogger(__name__)


class EditCategory(TemplateView, GetHeaderMixin):

    template_name = "category/edit_category.html"
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
        return super(EditCategory, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(EditCategory, self).get_context_data(**kwargs)
        category_id = context['categoryId']
        self.logger.info('========== Start get category  detail ==========')
        category_detail = self.get_category_detail(category_id)
        self.logger.info('========== Finish get category  detail ==========')
        self.logger.info('========== Start  product list of category ==========')
        product_in_category = self.get_products(category_id)
        self.logger.info('========== Finish get get product list of category ==========')
        context.update({
            "category": category_detail,
            'products': product_in_category
        })
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start edit category ==========')

        context = super(EditCategory, self).get_context_data(**kwargs)
        category_id = context['categoryId']
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
            body['is_active'] = True
        else:
            body['is_active'] = False

        url = api_settings.EDIT_CATEGORY.format(category_id=category_id)
        success, status_code, status_message, data = RestFulClient.put(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=body)
        API_Logger.put_logging(loggers=self.logger, params=body, response=data, status_code=status_code)
        if success:
            self.logger.info('========== Finish edit category ==========')
            self.logger.info('========== Start get category  detail ==========')
            category_detail = self.get_category_detail(category_id)
            self.logger.info('========== Finish get category  detail ==========')
            self.logger.info('========== Start  product list of category ==========')
            product_in_category = self.get_products(category_id)
            self.logger.info('========== Finish get get product list of category ==========')
            context.update({
                "category": category_detail,
                'products': product_in_category
            })
            messages.success(request, 'Edited Successfully')
            return render(request, self.template_name, context)
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(status_message))
            raise InvalidAccessToken(status_message)
        else:
            self.logger.info('========== Finish edit category ==========')
            self.logger.info('========== Start get category  detail ==========')
            category_detail = self.get_category_detail(category_id)
            self.logger.info('========== Finish get category  detail ==========')
            self.logger.info('========== Start  product list of category ==========')
            product_in_category = self.get_products(category_id)
            self.logger.info('========== Finish get get product list of category ==========')
            context.update({
                "category": category_detail,
                'products': product_in_category
            })
            return render(request, self.template_name, context)

    def get_category_detail(self, category_id):
        api_path = api_settings.GET_CATEGORIES

        body = {
            "id": category_id
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body,
                                                                        timeout=settings.GLOBAL_TIMEOUT)
        if data.get('categories'):
            data = data.get('categories')[0]
        else:
            data = {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=False)

        return data

    def get_products(self, category_id):
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

        data = data.get('products') or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=True)

        return data





