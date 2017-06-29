import logging
import time
import requests

from web_admin import api_settings
from django.views.generic.base import TemplateView
from web_admin.utils import setup_logger
from web_admin.restful_methods import RESTfulMethods


logger = logging.getLogger(__name__)


class CustomerDetailView(TemplateView, RESTfulMethods):
    template_name = 'customer_detail.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(CustomerDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting customer detail ==========')

        customer_id = int(kwargs.get('customerId'))
        data = self.get_member_detail(customer_id=customer_id)        
        self.logger.info('========== Finished getting customer detail ==========')

        return data
        
    def get_member_detail(self, customer_id):
        url = api_settings.MEMBER_CUSTOMER_PATH
        self.logger.info('API-Path: {}/{};'.format(url, customer_id))
        body = {
            'id': customer_id
        }
        data, success = self._post_method(api_path= url,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params=body)
        context = {'customer_info': data[0]}
        return context

                

