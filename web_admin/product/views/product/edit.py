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


class EditView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "product/edit.html"
    raise_exception = False
    logger = logger
    group_required = "CAN_EDIT_PRODUCT"
    login_url = 'web:permission_denied'

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        product_id = self.kwargs['product_id']

        self.logger.info('========== Start get product details ==========')
        params = {"id": product_id, 'paging': False}
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.GET_PRODUCT_DETAIL, headers=self._get_headers(), loggers=self.logger, params=params
        )
        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code, is_getting_list=False)
        self.logger.info('========== Finished get product details ==========')

        product = data['products'][0]
        if not product['denomination']:
            product['denomination'] = ['']

        product['product_category_id'] = product['product_category']['id']
        context = {"product": product}

        context['cbo_agent_types'] = self.get_agent_type(product_id)

        self.set_ui_list(context)

        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start edit product ==========')
        product_id = self.kwargs['product_id']
        is_active = request.POST.get('is_active') == 'on'
        name = request.POST.get('name')
        description = request.POST.get('description')
        image_url = request.POST.get('image_url')
        product_category_id = request.POST.get('product_category_id')
        product_category_id = int(product_category_id) if product_category_id else None
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
        denomination = self.filter_empty_denomination(denomination);

        params = {
            "id": product_id,
            "is_active": is_active,
            "name": name,
            "description": description,
            "image_url": image_url,
            "product_category_id": product_category_id,
            "payment_service_id": payment_service_id,
            "is_allow_price_range": is_allow_price_range,
            "max_price": max_price,
            "min_price": min_price,
            "denomination": denomination
        }

        is_success, status_code, status_message, data = RestFulClient.put(
            url=api_settings.EDIT_PRODUCT.format(product_id=product_id), headers=self._get_headers(), loggers=self.logger, params=params
        )

        API_Logger.put_logging(loggers=self.logger, params=params, response=data, status_code=status_code)
        self.logger.info('========== Finished edit product ==========')

        if not is_success:
            messages.error(request, status_message)
        else:
            self.delete_agent_types(product_id)
            self.mapping_product_agent_types(product_id, cbo_agent_types)
            messages.success(request, "Edited Successfully")
        context = {'product': params}
        context['cbo_agent_types'] = cbo_agent_types
        self.set_ui_list(context)
        return render(request, self.template_name, context)

    def filter_empty_denomination(self, denominations):
        denominations = list(filter(None, denominations))
        if not denominations:
            denominations = ['']
        return denominations

    def set_ui_list(self, context):
        self.logger.info('========== Start get category list ==========')
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.GET_CATEGORIES, headers=self._get_headers(), loggers=self.logger, params={}
        )
        categories = data['product_categories']
        categories = [x for x in categories if not x['is_deleted']]
        context['categories'] = categories
        API_Logger.post_logging(loggers=self.logger, params={}, response=categories, status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finished get category list ==========')

        self.logger.info('========== Start get service list ==========')
        is_success, status_code, data = RestFulClient.get(
            url=api_settings.SERVICE_LIST_URL, headers=self._get_headers(), loggers=self.logger
        )
        API_Logger.get_logging(loggers=self.logger, params={}, response=data, status_code=status_code)
        context['services'] = data
        self.logger.info('========== Finished get service list ==========')

        self.logger.info('========== Start get agent type list ==========')
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.AGENT_TYPES_LIST_URL, headers=self._get_headers(), loggers=self.logger, params={}
        )
        API_Logger.post_logging(loggers=self.logger, params={}, response=data, status_code=status_code, is_getting_list=True)
        context['agent_types'] = data
        self.logger.info('========== Finished get agent type list ==========')

    def get_agent_type(self, product_id):
        self.logger.info('========== Start get product - agent types relations ==========')
        params = {'product_id': product_id}
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.PRODUCT_AGENT_TYPE, headers=self._get_headers(), loggers=self.logger, params=params
        )
        relations = data['relations']
        API_Logger.post_logging(loggers=self.logger, params=params, response=relations, status_code=status_code, is_getting_list=True)
        self.logger.info('========== Finished get product - agent types relations ==========')

        agent_types = []
        for item in relations:
            agent_type_id = item['agent_type_id']
            agent_types.append(agent_type_id)

        return agent_types

    def delete_agent_types(self, product_id):
        self.logger.info('========== Start get product - agent types relations ==========')
        params = {'product_id': product_id}
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.PRODUCT_AGENT_TYPE, headers=self._get_headers(), loggers=self.logger,
            params=params
        )
        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code,
                                is_getting_list=False)
        self.logger.info('========== Finished get product - agent types relations ==========')

        relations = data['relations']
        for item in relations:
            product_agent_type_relation_id = item['id']
            self.logger.info('========== Start delete agent type relation ==========')
            is_success, status_code, status_message = RestFulClient.delete(
                url=api_settings.DELETE_PRODUCT_AGENT_TYPE_RELATION.format(product_agent_type_relation_id=product_agent_type_relation_id), headers=self._get_headers(), loggers=self.logger,
                params={}
            )
            API_Logger.delete_logging(loggers=self.logger, params={}, response={}, status_code=status_code)
            self.logger.info('========== Finished delete agent type relation ==========')

    def mapping_product_agent_types(self, product_id, agent_types):
        for agent_type_id in agent_types:
            body = {
                "product_id": product_id,
                "agent_type_id": agent_type_id
            }

            self.logger.info('========== Start creating product agent type mapping ==========')
            is_success, status_code, status_message, data = RestFulClient.post(
                url=api_settings.ADD_PRODUCT_AGENT_RELATION, headers=self._get_headers(), loggers=self.logger, params=body
            )
            API_Logger.post_logging(loggers=self.logger, params=body, response=data, status_code=status_code, is_getting_list=False)
            self.logger.info('========== Finished creating product agent type mapping ==========')

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])