import logging
import time
import requests

from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username
from web_admin.restful_methods import RESTfulMethods


logger = logging.getLogger(__name__)


class CustomerDetailView(TemplateView, RESTfulMethods):
    template_name = 'customer_detail.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CustomerDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting customer detail ==========')

        customer_id = int(kwargs.get('customerId'))
        data = self.get_member_detail(customer_id=customer_id)        
        self.logger.info('========== Finished getting customer detail ==========')

        return data
        
    def get_member_detail(self, customer_id):
        url = api_settings.MEMBER_CUSTOMER_PATH
        body = {
            'id': customer_id
        }
        data, success = self._post_method(api_path= url,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params=body)
        status = {
            True: 'Suspended',   # is_suspended == True
            False: 'Active'      # is_suspended == False
        }
        context = {'customer_info': data['customers'][0]}
        is_suspended = context['customer_info'].get('is_suspended')
        context['customer_info']['is_suspended'] = status[is_suspended]

        return context

                

