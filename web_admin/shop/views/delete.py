from django.shortcuts import render, redirect

from authentications.utils import get_correlation_id_from_username
from shop.utils import get_shop_details, convert_shop_to_form
from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from web_admin import api_settings, settings
from django.http import JsonResponse
from web_admin.api_settings import DELETE_PRODUCT
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, GetHeaderMixin):

    template_name = "shop/delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        shop_id = int(kwargs['id'])
        shop = get_shop_details(self, shop_id)
        form = convert_shop_to_form(shop)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        shop_id = int(kwargs['id'])
        url = api_settings.DELETE_SHOP.format(shop_id=shop_id)
        self.logger.info('========== Start delete shop ==========')
        success, status_code, status_message = RestFulClient.delete(url=url,
                                                                           headers=self._get_headers(),
                                                                           params={},
                                                                           loggers=self.logger)

        API_Logger.post_logging(loggers=self.logger, params={},
                                status_code=status_code, is_getting_list=False)
        self.logger.info('========== Finish delete shop ==========')
        if success:
            messages.success(request, 'Deleted data successfully')
            return redirect('shop:shop_list')
        else:
            messages.error(request, status_message)
            shop = get_shop_details(self, shop_id)
            form = convert_shop_to_form(shop)
            context = {'form': form}
            return render(request, self.template_name, context)
