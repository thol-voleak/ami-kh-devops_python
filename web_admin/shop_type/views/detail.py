from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings, settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from django.conf import settings
from braces.views import GroupRequiredMixin
from django.contrib import messages
from web_admin.api_settings import     GET_PRODUCT_DETAIL, GET_CATEGORIES, SERVICE_DETAIL_URL, PRODUCT_AGENT_TYPE, AGENT_TYPE_DETAIL_URL

logger = logging.getLogger(__name__)


class DetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "shop-type/detail.html"
    group_required = "CAN_VIEW_PRODUCT"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start render shop type detail ==========')
        context = super(DetailView, self).get_context_data(**kwargs)
        shop_type_id = int(context['id'])
        shop_type_detail = self.get_shop_type_detail(shop_type_id)
        context.update({
            'form': shop_type_detail['shop_types'][0]
        })
        self.logger.info('========== Finish render shop type detail ==========')
        return render(request, self.template_name, context)

    def get_shop_type_detail(self, shop_type_id):
        url = api_settings.GET_SHOP_TYPE_DETAIL
        body = {
            "id": shop_type_id
        }
        self.logger.info('========== Start get shop type detail ==========')
        success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)
        API_Logger.post_logging(loggers=self.logger, params=body,
                                status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finish get shop type detail ==========')
        return data
