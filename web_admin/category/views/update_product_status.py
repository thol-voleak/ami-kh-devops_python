from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.get_header_mixins import GetHeaderMixin
from django.views.generic.base import TemplateView
from web_admin import api_settings
from web_admin import ajax_functions
from web_admin.api_logger import API_Logger
from web_admin.restful_client import RestFulClient
from django.conf import settings
import logging


logger = logging.getLogger(__name__)


class UpdateProductStatusOfCategory(TemplateView, GetHeaderMixin):

    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UpdateProductStatusOfCategory, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = super(UpdateProductStatusOfCategory, self).get_context_data(**kwargs)
        logger = logging.getLogger(__name__)
        correlation_id = get_correlation_id_from_username(request.user)
        logger = setup_logger(request, logger, correlation_id)
        product_id = request.POST.get('product_id')
        product_status_get = request.POST.get('product_status')
        product_status = True if product_status_get == 'true' else False
        logger.info('========== Start getting product detail ==========')
        product_detail = self.get_product_detail(product_id)
        logger.info('========== Finish getting product detail ==========')
        body = {
            'is_active': product_status,
            "name": product_detail['name'],
            "description": product_detail['description'],
            "image_url": product_detail['image_url'],
            "denomination": product_detail['denomination'],
            "min_price": 0 if not product_detail['min_price'] else float(product_detail['min_price']),
            "max_price": 0 if not product_detail['max_price'] else float(product_detail['max_price']),
            "is_allow_price_range": product_detail['is_allow_price_range'],
            "category_id": product_detail['category_id'],
            "payment_service_id": product_detail['payment_service_id']
        }
        if product_status:
            logger.info('========== Start active product ==========')
        else:
            logger.info('========== Start inactive product ==========')
        url = api_settings.UPDATE_PRODUCT_STATUS_IN_CATEGORY.format(product_id=product_id)
        result = ajax_functions._put_method(request, url, "", logger, body)
        if product_status:
            logger.info('========== Finish active product ==========')
        else:
            logger.info('========== Finish inactive product ==========')
        return result

    def get_product_detail(self, product_id):
        api_path = api_settings.GET_PRODUCT_DETAIL

        body = {
            "id": product_id
        }

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body,
                                                                        timeout=settings.GLOBAL_TIMEOUT)

        data = data.get('products')[0] or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=False)

        return data