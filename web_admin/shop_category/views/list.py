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


class ListView(TemplateView, GetHeaderMixin):
    template_name = 'shop-category/list.html'
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        body = {
            "paging": True,
            "page_index": 1
        }

        shop_categories = self.get_shop_categories(body)
        
        page = shop_categories.get("page", {})
        context.update({
            'shop_categories': shop_categories['shop_categories'],
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page)
        })

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        opening_page_index = request.POST.get('current_page_index')

        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)

        shop_categories = self.get_shop_categories(body)
        page = shop_categories.get("page", {})

        context.update({
            'shop_categories': shop_categories['shop_categories'],
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page)
        })
        return render(request, self.template_name, context)

    def get_shop_categories(self, body):
        url = api_settings.GET_LIST_SHOP_CATEGORIES
        self.logger.info('========== Start get shop categories list ==========')
        success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        if data is None:
            data = {}
            data['shop_categories'] = []
        else:
            page = data.get("page", {})
            self.logger.info('Total element: {}'.format(page.get('total_elements', 0)))

        API_Logger.post_logging(loggers=self.logger, params=body,response=data['shop_categories'],
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get shop categories list ==========')
        return data
