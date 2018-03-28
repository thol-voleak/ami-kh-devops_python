from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.shortcuts import render, redirect
import logging

logger = logging.getLogger(__name__)


class DetailView(TemplateView, GetHeaderMixin):

    template_name = "shop-category/detail.html"
    # group_required = "CAN_VIEW_PRODUCT"
    login_url = 'web:permission_denied'
    # raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    # def check_membership(self, permission):
    #     self.logger.info(
    #         "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
    #     return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting shop category detail ==========')
        context = super(DetailView, self).get_context_data(**kwargs)
        id = context.get('id')
        if not id:
            return redirect('shop_category:shop_category_list')

        success, status_code, message, data = self.get_shop_category_detail(id)
        if not success:
            return redirect('shop_category:shop_category_list')

        context['form'] = data[0] if data else {}
        self.logger.info('========== Finish getting shop category detail ==========')
        return render(request, self.template_name, context)

    def get_shop_category_detail(self, id):
        params = {'id': id}
        success, status_code, message, data = RestFulClient.post(
            url=api_settings.GET_LIST_SHOP_CATEGORIES,
            params=params, loggers=self.logger,
            headers=self._get_headers()
        )
        API_Logger.post_logging(loggers=self.logger, params=params,
                                response=data,
                                status_code=status_code)
        return success, status_code, message, data.get('shop_categories')
