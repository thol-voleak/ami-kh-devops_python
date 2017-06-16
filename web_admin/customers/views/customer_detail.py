import logging
import time
import requests

from web_admin import api_settings
from django.views.generic.base import TemplateView

from web_admin.restful_methods import RESTfulMethods


logger = logging.getLogger(__name__)


class CustomerDetailView(TemplateView, RESTfulMethods):
    template_name = 'customer_detail.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting customer detail ==========')

        customer_id = int(kwargs.get('customerId'))
        data = self.get_member_detail(customer_id=customer_id)        
        logger.info('========== Finished getting customer detail ==========')

        return data
        
    def get_member_detail(self, customer_id):
        url = api_settings.MEMBER_CUSTOMER_PATH
        logger.info('API-Path: {}/{};'.format(url, customer_id))
        data, success = self._post_method(api_path= url,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params={})
        for i in data:
            if i['id'] == customer_id:
                context = {'customer_info': i}
                return context

