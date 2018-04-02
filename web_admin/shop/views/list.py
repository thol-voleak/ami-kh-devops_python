from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from shop.utils import get_all_shop_type, get_all_shop_category, search_shop
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from django.shortcuts import render
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import calculate_page_range_from_page_info


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

        shops = search_shop(self, params)
        page = shops.get('page', {})
        context.update({
            'shops': shops.get('shops', []),
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page),
            'total_result': page.get('total_elements', 0)
        })

        return render(request, self.template_name, context)