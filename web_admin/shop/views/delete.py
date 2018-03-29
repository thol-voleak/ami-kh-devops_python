from django.shortcuts import render

from authentications.utils import get_correlation_id_from_username
from shop.utils import get_shop_details, convert_shop_to_form
from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.http import JsonResponse
from web_admin.api_settings import DELETE_PRODUCT
import logging


logger = logging.getLogger(__name__)


class DeleteView(TemplateView, GetHeaderMixin):

    template_name = "shop/delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        shop = get_shop_details(self, id)
        form = convert_shop_to_form(shop)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs['id']
        # TODO: call delete API
        form = request.POST
        context = {'form': form}
        return render(request, self.template_name, context)