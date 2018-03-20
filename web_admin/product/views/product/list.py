from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger

from django.views.generic.base import TemplateView
from django.conf import settings
from django.shortcuts import render
from datetime import datetime , timedelta
from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.api_logger import API_Logger


import logging

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_MANAGE_PRODUCT"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'product/list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        permissions = {}
        permissions['CAN_ADD_PRODUCT'] = self.check_membership(["CAN_ADD_PRODUCT"])
        permissions['CAN_EDIT_PRODUCT'] = self.check_membership(["CAN_EDIT_PRODUCT"])
        permissions['CAN_DELETE_PRODUCT'] = self.check_membership(["CAN_DELETE_PRODUCT"])
        permissions['CAN_VIEW_PRODUCT'] = self.check_membership(["CAN_VIEW_PRODUCT"])

        params = {}
        products = {}
        is_success = False
        status_code = ''
        url = api_settings.GET_PRODUCTS
        context = super(ListView, self).get_context_data(**kwargs)
        categories = self._list_categories()
        if categories:
            categories = categories['categories']
            categories.insert(0, {'name':'All'})
            context['categories'] = categories
        else:
            context['categories'] = [{'name':'All'}]
        self.logger.info('========== Start searching products ==========')
        opening_page_index = request.GET.get('current_page_index')
        product_id = request.GET.get('product_id')
        category_id = request.GET.get('category_id')
        product_name = request.GET.get('product_name')
        product_status = request.GET.get('product_status')
        if product_id is None and category_id is None \
           and product_name is None and product_status is None:
           products = {}
           context['search_count'] = 0
        else:
            params['paging'] = True
            params['page_index'] = int(opening_page_index)
            if product_id:
                product_id = int(product_id)
                params['id'] = product_id
                context['product_id'] = product_id
            if category_id:
                category_id = int(category_id)
                params['category_id'] = category_id
                context['category_id'] = category_id
            if product_name:
                params['name'] = product_name
                context['product_name'] = product_name
            if product_status and isinstance(product_status, str):
                if product_status.lower() == "true":
                    product_status = True
                else:
                    product_status = False
                params['is_active'] = product_status
                context['product_status'] = product_status
            params['is_deleted'] = False
            self.logger.info("Params: {} ".format(params))
            is_success, status_code, status_message, data = RestFulClient.post(
                                                    url= url,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=params)
            self.logger.info("Params: {} ".format(params))
        if is_success:
            products = data['products']
            page = data['page']
            count = len(products)
            self.logger.info("Response_content_count:{}".format(count))
            context.update({'paginator': page, 'page_range': calculate_page_range_from_page_info(page)})
            context['search_count'] = page['total_elements']
            context['data'] = products
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

        context['permissions'] = permissions
            
        self.logger.info('========== Finished searching products ==========')
        return render(request, self.template_name, context)

    def _list_categories(self):
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

        if success:
            return data
        else:
            return None
