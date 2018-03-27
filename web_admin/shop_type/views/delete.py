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

    template_name = "shop-type/delete.html"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        self.logger.info('========== User go to Delete shop type page ==========')
        id = context.get('id')
        if not id:
            return redirect('shop_type:shop_type_list')

        success, status_code, message, data = self.get_shop_type_detail(id)
        if not success:
            return redirect('shop_type:shop_type_list')

        context['form'] = data[0] if data else {}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting shop type ==========')
        context = super(DeleteView, self).get_context_data(**kwargs)
        id = context.get('id')

        success, status_code, message = self.delete_shop_type(id)
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Deleted data successfully'
            )

        self.logger.info('========== Finish deleting shop type ==========')
        return redirect('shop_type:shop_type_list')

    def delete_shop_type(self, id):
        success, status_code, message = RestFulClient.delete(
            url=api_settings.SHOP_TYPE_DELETE.format(shop_type_id=id),
            loggers=self.logger, headers=self._get_headers()
        )
        API_Logger.delete_logging(loggers=self.logger,
                                  status_code=status_code)
        return success, status_code, message

    def get_shop_type_detail(self, id):
        self.logger.info('========== Start getting shop type detail ==========')
        params = {'id': id}
        success, status_code, message, data = RestFulClient.post(
            url=api_settings.GET_SHOP_TYPE_DETAIL,
            params=params, loggers=self.logger,
            headers=self._get_headers()
        )
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish getting shop type detail ==========')
        return success, status_code, message, data.get('shop_types')