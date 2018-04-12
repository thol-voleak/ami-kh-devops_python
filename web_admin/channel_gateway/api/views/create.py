from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_helper import RestfulHelper
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render, redirect
from django.contrib import messages
import logging
from channel_gateway.api.utils  import get_service_list

logger = logging.getLogger(__name__)


class CreateView(TemplateView, GetHeaderMixin):
    template_name = "channel-gateway-api/create.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(
                self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        body_res = {
            'is_deleted': False,
            'paging': False
        }
        service_list = get_service_list(self, body_res)
        context.update({
            'service_list': service_list.get('services', [])
        })
        return render(request, self.template_name, context)
