import logging
import time
import requests

from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username
from web_admin.restful_methods import RESTfulMethods

from customers.views import CustomerAPIService

logger = logging.getLogger(__name__)


class CustomerDetailView(TemplateView, RESTfulMethods, CustomerAPIService):
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

        # Convert date format
        date_of_birth = context['customer_info']['date_of_birth']
        if date_of_birth:
            context['customer_info']['date_of_birth'] = date_of_birth.split('T')[0]

        primary_issue_date = context['customer_info']['kyc']['primary_identity']['issue_date']
        if primary_issue_date:
            context['customer_info']['kyc']['primary_identity']['issue_date'] = primary_issue_date.split('T')[0]
        primary_expiry_date = context['customer_info']['kyc']['primary_identity']['expired_date']
        if primary_expiry_date:
            context['customer_info']['kyc']['primary_identity']['expired_date'] = primary_expiry_date.split('T')[0]

        secondary_issue_date = context['customer_info']['kyc']['secondary_identity']['issue_date']
        if secondary_issue_date:
            context['customer_info']['kyc']['secondary_identity']['issue_date'] = secondary_issue_date.split('T')[0]
        secondary_expiry_date = context['customer_info']['kyc']['secondary_identity']['expired_date']
        if secondary_expiry_date:
            context['customer_info']['kyc']['secondary_identity']['expired_date'] = secondary_expiry_date.split('T')[0]

        tertiary_issue_date = context['customer_info']['kyc']['tertiary_identity']['issue_date']
        if tertiary_issue_date:
            context['customer_info']['kyc']['tertiary_identity']['issue_date'] = tertiary_issue_date.split('T')[0]
        tertiary_expiry_date = context['customer_info']['kyc']['tertiary_identity']['expired_date']
        if tertiary_expiry_date:
            context['customer_info']['kyc']['tertiary_identity']['expired_date'] = tertiary_expiry_date.split('T')[0]

        kyc_verify_date = context['customer_info']['kyc']['verify_date']
        if kyc_verify_date:
            context['customer_info']['kyc']['verify_date'] = kyc_verify_date.split('T')[0]

        # get MM card type
        mm_card_type_id = context['customer_info']['mm_card_type_id']
        if mm_card_type_id:
            mm_card_type = self.get_mm_card_type(mm_card_type_id)
            if mm_card_type:
                context['customer_info']['mm_card_type_name'] = mm_card_type[0]['name']

        # get MM card level
        mm_card_level_id = context['customer_info']['mm_card_level_id']
        if mm_card_level_id:
            mm_card_level = self.get_mm_card_level(mm_card_level_id)
            if mm_card_level:
                context['customer_info']['mm_card_level_name'] = mm_card_level[0]['level']

        # get classification
        classification_id = context['customer_info']['customer_classification_id']
        if classification_id:
            classification = self.get_classification(classification_id)
            if classification:
                context['customer_info']['customer_classification_name'] = classification[0]['name']

        # get KYC level
        kyc_level_id = context['customer_info']['kyc']['level']
        if kyc_level_id:
            kyc_level = self.get_kyc_level(kyc_level_id)
            if kyc_level:
                context['customer_info']['kyc']['level_name'] = kyc_level[0]['level']

        return context
