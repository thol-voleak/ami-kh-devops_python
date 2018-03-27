from django.shortcuts import render

from authentications.utils import get_correlation_id_from_username
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

    template_name = "shop-category/delete.html"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = {"id": 123, "name": "Name", "description": "Description"}
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = request.POST
        context = {'form': form}
        return render(request, self.template_name, context)