from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from django.http import JsonResponse
from web_admin.api_settings import DELETE_PRODUCT
import logging


logger = logging.getLogger(__name__)


class ProductDelete(TemplateView, GetHeaderMixin):

    template_name = "product/detail.html"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ProductDelete, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting products ==========')
        produce_ids = request.POST.getlist('ids[]')

        success_ids = []
        failed_count = 0
        for id in produce_ids:
            success, status_code, message = self.delete_product(id)
            if status_code in ["access_token_expire", "authentication_fail", "invalid_access_token"]:
                return JsonResponse({"invalid_access_token": True})

            if success:
                success_ids.append(id)
            else:
                failed_count += 1
        self.logger.info('========== Finish deleting products ==========')

        return JsonResponse({"success_ids": success_ids, "failed_count": failed_count})

    def delete_product(self, product_id):
        self.logger.info('========== Start deleting product [{}] =========='.format(product_id))
        success, status_code, message = RestFulClient.delete(
            url=DELETE_PRODUCT.format(product_id=product_id),
            loggers=self.logger,
            headers=self._get_headers()
        )

        self.logger.info('========== Finish deleting product [{}] =========='.format(product_id))

        return success, status_code, message