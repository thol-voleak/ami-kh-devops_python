from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger

from django.views.generic.base import TemplateView
from django.contrib import messages
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from shop.utils import get_shop_details, convert_shop_to_form, convert_form_to_shop
from django.http import HttpResponseRedirect

import logging

logger = logging.getLogger(__name__)


class UnLinkAgentToShop(TemplateView, GetHeaderMixin):
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UnLinkAgentToShop, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(UnLinkAgentToShop, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        shop_id = context['shop_id']
        shop_detail = get_shop_details(self, int(shop_id))
        self.logger.info('========== Start unlink shop from Agent ==========')
        form = convert_shop_to_form(shop_detail)
        converted_shop = convert_form_to_shop(form)
        converted_shop['agent_id'] = None
        params = converted_shop
        url = api_settings.EDIT_SHOP.format(shop_id=shop_id)
        is_success, status_code, status_message, data = RestFulClient.put(url,
                                                                          self._get_headers(),
                                                                          self.logger, params)
        API_Logger.put_logging(loggers=self.logger, params=params, response=data,
                               status_code=status_code)
        if is_success:
            messages.add_message(request, messages.SUCCESS, 'Successfully un-linked ' + shop_detail['name'] + ' from Agent ID ' + agent_id)
        self.logger.info('========== Finish unlink shop from Agent ==========')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



