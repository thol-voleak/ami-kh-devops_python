from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin import setup_logger, api_settings
from web_admin.utils import calculate_page_range_from_page_info
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


class ShopTypeList(TemplateView, GetHeaderMixin):

    template_name = "shop-type/list.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ShopTypeList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ShopTypeList, self).get_context_data(**kwargs)
        self.logger.info('========== Start render shop type page ==========')
        body = {
            "paging": True,
            "page_index": 1
        }

        shop_types = self.get_shop_type(body)
        
        page = shop_types.get("page", {})
        context.update({
            'shop_types': shop_types['shop_types'],
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page)
        })
        self.logger.info('========== Finish render shop type page ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(ShopTypeList, self).get_context_data(**kwargs)
        opening_page_index = request.POST.get('current_page_index')

        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)

        shop_types = self.get_shop_type(body)
        page = shop_types.get("page", {})

        context.update({
            'shop_types': shop_types['shop_types'],
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page)
        })
        return render(request, self.template_name, context)


    def get_shop_type(self, body):
        url = api_settings.GET_LIST_SHOP_TYPE
        self.logger.info('========== Start get shop type list ==========')
        success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        API_Logger.post_logging(loggers=self.logger, params=body,response=data.get('shop_types'),
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get shop type list ==========')
        return data
