from web_admin import api_settings
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render
from channel_gateway.api.utils import get_api_detail
from web_admin.utils import check_permissions, build_logger
from web_admin.restful_helper import RestfulHelper
import logging


logger = logging.getLogger(__name__)

class DetailView(TemplateView, GetHeaderMixin):
    template_name = "channel-gateway-api/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_VIEW_GW_API")
        self.logger = build_logger(request, __name__)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        api_id = int(kwargs['id'])
        api = get_api_detail(self, api_id)
        context = {
            "form": api
        }
        return render(request, self.template_name, context)

