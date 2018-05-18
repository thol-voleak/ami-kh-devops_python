from web_admin import api_settings
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render
import logging
from web_admin.utils import check_permissions, build_logger
from web_admin.restful_helper import RestfulHelper

logger = logging.getLogger(__name__)


class DetailView(TemplateView, GetHeaderMixin):

    template_name = "channel-gateway-service/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_VIEW_GW_SERVICE")
        self.logger = build_logger(request, __name__)
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
        if not data:
            return {}
        return data["services"][0]
        