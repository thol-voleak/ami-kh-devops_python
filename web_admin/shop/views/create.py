from django.urls import reverse

from shop.utils import get_all_shop_type, get_all_shop_category, get_system_country, convert_form_to_shop, \
    get_agent_detail
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from web_admin import setup_logger
from web_admin import api_settings, RestFulClient
from django.contrib import messages
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
import logging
from web_admin.api_logger import API_Logger
from web_admin.utils import get_back_url

logger = logging.getLogger(__name__)


class CreateView(TemplateView, RESTfulMethods):
    template_name = "shop/create.html"
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def get(self, request, *args, **kwargs):
        form = {}

        agent_id = request.GET["agent_id"]
        if agent_id:
            agent = get_agent_detail(self, int(agent_id))
            form["representative_first_name"] = agent["firstname"]
            form["representative_last_name"] = agent["lastname"]
            form["representative_mobile_number"] = agent["primary_mobile_number"]
            form["representative_email"] = agent["email"]
            form["shop_mobile_number"] = agent["primary_mobile_number"]
            form["shop_email"] = agent["email"]

        context = {'form': form}

        list_shop_type = get_all_shop_type(self)
        context['list_shop_type'] = list_shop_type

        list_shop_category = get_all_shop_category(self)
        context['list_shop_category'] = list_shop_category

        country = get_system_country(self)
        form['country'] = country

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = request.POST
        context = {'form': form}

        list_shop_type = get_all_shop_type(self)
        context['list_shop_type'] = list_shop_type

        list_shop_category = get_all_shop_category(self)
        context['list_shop_category'] = list_shop_category

        shop = convert_form_to_shop(form)
        # TODO: call create shop API

        # IF SUCCESS
        messages.success(request, "Added Successfully")
        return redirect(get_back_url(request, reverse('shop:shop_list')))

        # IF FAIL
        return render(request, self.template_name, context)