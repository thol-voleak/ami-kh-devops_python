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
from web_admin.restful_helper import RestfulHelper
import logging

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, GetHeaderMixin):
    template_name = "channel-gateway-service/delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        services_id = int(kwargs['id'])
        services = self.get_service_detail(services_id)
        context = {
            "form": services
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        services_id = int(kwargs['id'])
        api_path = api_settings.DELETE_CHANNEL_SERVICE.format(service_id=services_id)
        success, status_code, status_message, data = RestfulHelper.send("DELETE", api_path, {}, self.request, "delete service")

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Service has been deleted'
            )
            return redirect('channel_gateway_service:list')
        else:
            messages.add_message(request, messages.ERROR, status_message)
            services = self.get_service_detail(services_id)
            context = {
                "form": services
            }
            return render(request, self.template_name, context)

    def get_service_detail(self, services_id):
        url = api_settings.GET_CHANNEL_SERVICE
        params = {
            "id": services_id
        }
        is_success, status_code, status_message, data = RestfulHelper.send("POST", url, params, self.request, "get service detail")
        if data is None:
            return None
        return data["services"][0]
