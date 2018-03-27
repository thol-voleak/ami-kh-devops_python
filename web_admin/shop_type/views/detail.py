from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from django.conf import settings
from braces.views import GroupRequiredMixin
from django.contrib import messages
from web_admin.api_settings import     GET_PRODUCT_DETAIL, GET_CATEGORIES, SERVICE_DETAIL_URL, PRODUCT_AGENT_TYPE, AGENT_TYPE_DETAIL_URL

logger = logging.getLogger(__name__)


class DetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "shop-type/detail.html"
    group_required = "CAN_VIEW_PRODUCT"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        form = {"id": 123, "name": "Name", "description": "Description"}
        context = {'form': form}
        return render(request, self.template_name, context)
