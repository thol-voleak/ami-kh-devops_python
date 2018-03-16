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


class CreateView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "product/create.html"
    group_required = "CAN_ADD_PRODUCT"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        self.set_ui_list(context)

        # Set default data
        product = {
            "is_active": False,
            "is_allow_price_range": True,
            "denomination": ['']
        }
        context['product'] = product

        return context

    def post(self, request, *args, **kwargs):
        is_active = request.POST.get('is_active') == 'on'
        name = request.POST.get('name')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        category_id = request.POST.get('category_id')
        category_id = int(category_id) if category_id else None
        payment_service_id = request.POST.get('payment_service_id')
        payment_service_id = int(payment_service_id) if payment_service_id else None
        is_allow_price_range = request.POST.get('is_allow_price_range') == 'on'
        max_price = request.POST.get('max_price')
        max_price = float(max_price) if is_allow_price_range and max_price else None
        min_price = request.POST.get('min_price')
        min_price = float(min_price) if is_allow_price_range and min_price else None
        cbo_agent_types = request.POST.getlist('cbo_agent_types')
        cbo_agent_types = list(map(int, cbo_agent_types))  # convert list string to list int
        denomination = request.POST.getlist('denomination')

        params = {
            "is_active": is_active,
            "name": name,
            "description": description,
            "image_url": image_url,
            "category_id": category_id,
            "payment_service_id": payment_service_id,
            "is_allow_price_range": is_allow_price_range,
            "max_price": max_price,
            "min_price": min_price,
            "denomination": denomination
        }

        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.ADD_PRODUCT, headers=self._get_headers(), loggers=self.logger, params=params
        )

        if not is_success:
            messages.error(request, status_message)
            context = {'product': params}
            context['cbo_agent_types'] = cbo_agent_types
            self.set_ui_list(context)
            return render(request, self.template_name, context)

        product_id = data['id']
        for agent_type_id in cbo_agent_types:
            body = {
                "product_id": product_id,
                "agent_type_id": agent_type_id
            }

            is_success, status_code, status_message, data = RestFulClient.post(
                url=api_settings.ADD_PRODUCT_AGENT_RELATION, headers=self._get_headers(), loggers=self.logger, params=body
            )

        messages.success(request, "Added Successfully")
        return redirect('product:product_create')

    def set_ui_list(self, context):
        # Get list category
        data, success = self._post_method(api_path=api_settings.GET_CATEGORIES, logger=logger)
        context['categories'] = data['categories']

        # Get list service
        data, success = self._get_method(api_path=api_settings.SERVICE_LIST_URL, logger=logger)
        context['services'] = data

        # Get list agent type
        data, success = self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL, logger=logger)
        context['agent_types'] = data

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])