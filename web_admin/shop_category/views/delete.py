from django.shortcuts import render, redirect
from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.contrib import messages
import logging


logger = logging.getLogger(__name__)


class DeleteView(TemplateView, GetHeaderMixin):

    template_name = "shop-category/delete.html"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start rendering delete shop category page ==========')
        context = super(DeleteView, self).get_context_data(**kwargs)
        id = context.get('id')
        if not id:
            return redirect('shop_category:shop_category_list')

        success, status_code, message, data = self.get_shop_category_detail(id)
        if not success:
            return redirect('shop_category:shop_category_list')

        context['form'] = data[0] if data else {}
        self.logger.info('========== Finish rendering delete shop category page ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting shop category ==========')
        context = super(DeleteView, self).get_context_data(**kwargs)
        id = context.get('id')

        success, status_code, message = self.delete_shop_category(id)
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Deleted data successfully'
            )

        self.logger.info('========== Finish deleting shop category ==========')
        return redirect('shop_category:shop_category_list')

    def delete_shop_category(self, id):
        success, status_code, message = RestFulClient.delete(
            url=api_settings.DELETE_SHOP_CATEGORY.format(shop_category_id=id),
            loggers=self.logger, headers=self._get_headers()
        )
        API_Logger.delete_logging(loggers=self.logger,
                                  status_code=status_code)
        return success, status_code, message

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