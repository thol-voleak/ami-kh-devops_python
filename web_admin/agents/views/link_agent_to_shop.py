from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger

from django.views.generic.base import TemplateView
from django.contrib import messages
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from shop.utils import get_shop_details
from django.http import HttpResponseRedirect

import logging

logger = logging.getLogger(__name__)


class LinkAgentToShop(TemplateView, GetHeaderMixin):
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(LinkAgentToShop, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(LinkAgentToShop, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        shop_id = context['shop_id']
        shop_detail = get_shop_details(self, int(shop_id))
        self.logger.info('========== Start link shop to Agent ==========')
        shop_type_id = None
        if shop_detail['shop_type']:
            shop_type_id = shop_detail['shop_type'].get('id', None)

        shop_category_id = None
        if shop_detail['shop_category']:
            shop_category_id = shop_detail['shop_category'].get('id', None)

        params = {
              "agent_id": int(agent_id),
              "shop_type_id": shop_type_id,
              "name": shop_detail['name'],
              "shop_category_id": shop_category_id,
              "address": {
                "address": shop_detail['address'].get('address'),
                "city": shop_detail['address'].get('city'),
                "province": shop_detail['address'].get('province'),
                "district": shop_detail['address'].get('district'),
                "commune": shop_detail['address'].get('commune'),
                "country": shop_detail['address'].get('country'),
                "landmark": shop_detail['address'].get('landmark'),
                "latitude": shop_detail['address'].get('latitude'),
                "longitude": shop_detail['address'].get('longitude')
              },
              "relationship_manager_id": shop_detail.get('relationship_manager_id'),
              "acquisition_source": shop_detail.get('acquisition_source'),
              "postal_code": shop_detail.get('postal_code'),
              "representative_first_name": shop_detail.get('representative_first_name'),
              "representative_middle_name": shop_detail.get('representative_middle_name'),
              "representative_last_name": shop_detail.get('representative_last_name'),
              "representative_mobile_number": shop_detail.get('representative_mobile_number'),
              "representative_telephone_number": shop_detail.get('representative_telephone_number'),
              "representative_email": shop_detail.get('representative_email'),
              "shop_mobile_number": shop_detail.get('shop_mobile_number'),
              "shop_telephone_number": shop_detail.get('shop_telephone_number'),
              "shop_email": shop_detail.get('shop_email'),
              "relationship_manager_name": shop_detail.get('relationship_manager_name'),
              "relationship_manager_email": shop_detail.get('relationship_manager_email'),
              "acquiring_sales_executive_name": shop_detail.get('acquiring_sales_executive_name'),
              "sales_region": shop_detail.get('sales_region'),
              "account_manager_name": shop_detail.get('account_manager_name')
        }
        url = api_settings.EDIT_SHOP.format(shop_id=shop_id)
        is_success, status_code, status_message, data = RestFulClient.put(url,
                                                                          self._get_headers(),
                                                                          self.logger, params)
        API_Logger.put_logging(loggers=self.logger, params=params, response=data,
                               status_code=status_code)
        if is_success:
            messages.add_message(request, messages.SUCCESS, 'Successfully added ' + shop_detail['name'] + ' to Agent ID ' + agent_id)
        self.logger.info('========== Finish link shop to Agent ==========')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



