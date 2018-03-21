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


class ProductDetail(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "product/detail.html"
    group_required = "CAN_VIEW_PRODUCT"
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ProductDetail, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting product details ==========')
        context = super(ProductDetail, self).get_context_data(**kwargs)
        product_id = context['product_id']
        data = self.get_product_detail(product_id)
        category_name = ""
        service_name = ""
        if data:
            category_id = data.get('category_id', None)
            if category_id:
                category_name = self.get_category_name(category_id)

            payment_service_id = data.get('payment_service_id', None)
            if payment_service_id:
                service_name = self.get_service_name(payment_service_id)

            agent_types = self.get_agent_type(product_id)

        self.logger.info('========== Fisnish getting product details ==========')

        has_denomination = False
        if len(data["denomination"]) >= 1:
            has_denomination = True

        has_agent_types = False
        if len(agent_types) >= 1:
            has_agent_types = True

        context.update({
            'product': data,
            'category_name': category_name,
            'service_name': service_name,
            'agent_types': agent_types,
            'has_denomination': has_denomination,
            'has_agent_types': has_agent_types,
        })

        return render(request, self.template_name, context)

    def get_product_detail(self, product_id):
        url = GET_PRODUCT_DETAIL
        params = {
            'id': product_id,
            'paging': False,
        }
        is_success, status_code, status_message, data= RestFulClient.post(url=url, 
                                                                            headers=self._get_headers(), 
                                                                            loggers=self.logger, 
                                                                            params=params,
                                                                            timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                        status_code=status_code)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            return None
        return data['products'][0]

    def get_category_name(self, category_id):
        self.logger.info('========== Start getting category details ==========')
        url = GET_CATEGORIES
        params = {
            'id': category_id,
            'paging': False,
        }
        is_success, status_code, status_message, data= RestFulClient.post(url=url,
                                                                            headers=self._get_headers(),
                                                                            loggers=self.logger,
                                                                            params=params,
                                                                            timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                        status_code=status_code)

        self.logger.info('========== Finish getting category details ==========')

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            return str(category_id)
        return data['categories'][0]['name']

    def get_service_name(self, service_id):
        self.logger.info('========== Start getting service name ==========')
        url = SERVICE_DETAIL_URL.format(service_id)
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger,
                                                       headers=self._get_headers())
        
        self.logger.info('========== End getting service name ==========')

        if not success:
            messages.add_message(
                self.request,
                messages.ERROR,
                "Failed to get service name"
            )
            return str(service_id)
        return data['service_name']

    def get_agent_type(self, product_id):
        self.logger.info('========== Start getting agent type id ==========')
        url = PRODUCT_AGENT_TYPE
        params = {
            'product_id': product_id,
        }
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish getting agent type id ==========')

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            return []
        relations = data['relations']
        agent_types = []
        for item in relations:
            agent_type_id = item['agent_type_id']
            agent_type_name = self.get_agent_type_name(agent_type_id)
            agent_types.append(agent_type_name)

        return agent_types



    def get_agent_type_name(self, agent_type_id):
        self.logger.info('========== Start getting agent type name ==========')
        params = {"id": agent_type_id}
        url = AGENT_TYPE_DETAIL_URL
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish getting agent type name ==========')
        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            return str(agent_type_id)

        return data[0]['name']



