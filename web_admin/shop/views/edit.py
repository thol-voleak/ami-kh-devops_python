from shop.utils import get_shop_details, convert_shop_to_form, convert_form_to_shop
from web_admin.api_logger import API_Logger
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient
from django.contrib import messages
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
import logging

logger = logging.getLogger(__name__)


class EditView(TemplateView, RESTfulMethods):
    template_name = "shop/edit.html"
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        shop = get_shop_details(self, id)
        form = convert_shop_to_form(shop)
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs['id']
        form = request.POST
        shop = convert_form_to_shop(form)
        # TODO: call API
        context = {'form': form}
        return render(request, self.template_name, context)