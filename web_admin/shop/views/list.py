from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from shop.utils import get_all_shop_type, get_all_shop_category
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
    template_name = 'shop/list.html'
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = request.GET
        context = {"form": form}
        self.logger.info('========== Start getting all shop types ==========')
        list_shop_type = get_all_shop_type(self)
        self.logger.info('========== Finish getting all shop types ==========')
        context['list_shop_type'] = list_shop_type

        self.logger.info('========== Start getting all shop categories ==========')
        list_shop_category = get_all_shop_category(self)
        self.logger.info('========== Finish getting all shop categories ==========')
        context['list_shop_category'] = list_shop_category
        opening_page_index = form.get('current_page_index', 1)

        params = {
            "paging": True,
            "page_index": int(opening_page_index)
        }
        if form.get('shop_id'):
            params['id'] = int(form['shop_id'])

        if form.get('shop_category'):
            params['shop_category_id'] = int(form['shop_category'])

        if form.get('shop_name'):
            params['name'] = form['shop_name']

        if form.get('shop_type'):
            params['shop_type_id'] = int(form['shop_type'])

        if form.get('relationship_manager'):
            params['relationship_manager_name'] = form['relationship_manager']

        if form.get('owner_id'):
            params['agent_id'] = form['owner_id']

        shops = self.search_shop(params)
        page = shops.get('page', {})
        context.update({
            'shops': shops.get('shops', []),
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page)
        })

        return render(request, self.template_name, context)

    def search_shop(self, params):
        self.logger.info('========== Start searching shop ==========')
        api_path = api_settings.SEARCH_SHOP
        success, status_code, status_message, data = RestFulClient.post(
            url=api_path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params
        )

        data = data or {}
        page = data.get("page", {})
        self.logger.info(
            'Total element: {}'.format(page.get('total_elements', 0)))
        API_Logger.post_logging(loggers=self.logger,
                                response=data.get('shops', []),
                                status_code=status_code,
                                is_getting_list=True,
                                params=params)
        self.logger.info('========== Finish searching shop ==========')
        return data