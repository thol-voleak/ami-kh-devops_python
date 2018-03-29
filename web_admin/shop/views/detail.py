from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from shop.utils import get_shop_details, convert_shop_to_form
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

logger = logging.getLogger(__name__)


class DetailView(TemplateView, GetHeaderMixin):

    template_name = "shop/detail.html"
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        shop_id = kwargs['id']
        shop = get_shop_details(self, shop_id)
        form = convert_shop_to_form(shop)
        context = {'form': form}
        return render(request, self.template_name, context)
