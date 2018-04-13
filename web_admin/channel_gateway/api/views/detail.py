from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render
from channel_gateway.api.utils import get_api_detail
import logging

from web_admin.restful_helper import RestfulHelper

logger = logging.getLogger(__name__)


class DetailView(TemplateView, GetHeaderMixin):
    template_name = "channel-gateway-api/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        api_id = int(kwargs['id'])
        api = get_api_detail(self, api_id)
        context = {
            "form": api
        }
        return render(request, self.template_name, context)

