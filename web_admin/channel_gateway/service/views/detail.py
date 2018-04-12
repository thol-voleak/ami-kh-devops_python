from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from authentications.apps import InvalidAccessToken
from django.shortcuts import render, redirect
from django.contrib import messages
from web_admin.api_logger import API_Logger
from django.http import JsonResponse
import logging

from web_admin.restful_helper import RestfulHelper

logger = logging.getLogger(__name__)


class DetailView(TemplateView, GetHeaderMixin):

    template_name = "channel-gateway-service/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        services_id = int(kwargs['id'])
        service  = self.get_service_detail(services_id)
        context = {
            "form" : service
        }
        return render(request, self.template_name, context)

    def get_service_detail(self, services_id):
        url = api_settings.GET_CHANNEL_SERVICE
        params = {
            "id": services_id
        }
        is_success, status_code, status_message, data = RestfulHelper.send("POST", url, params, self.request, "get service detail")
        if data is None:
            return None;
        return data["services"][0]
        