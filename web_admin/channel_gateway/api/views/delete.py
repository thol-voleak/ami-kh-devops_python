from web_admin.utils import check_permissions, build_logger
from web_admin import setup_logger, api_settings
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from web_admin.restful_helper import RestfulHelper
from channel_gateway.api.utils import get_api_detail
import logging

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, GetHeaderMixin):
    template_name = "channel-gateway-api/delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_DELETE_GW_API")
        self.logger = build_logger(request, __name__)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        api_id = int(kwargs['id'])
        api = get_api_detail(self,api_id)
        context = {
            "form": api
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        api_id = int(kwargs['id'])
        api_path = api_settings.DELETE_CHANNEL_API.format(api_id=api_id)
        success, status_code, status_message, data = RestfulHelper.send("DELETE", api_path, {}, self.request, "delete api")

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'API has been deleted'
            )
            return redirect('channel_gateway_api:list')
        else:
            messages.add_message(request, messages.ERROR, status_message)
            api = get_api_detail(self, api_id)
            context = {
                "form": api
            }
            return render(request, self.template_name, context)

