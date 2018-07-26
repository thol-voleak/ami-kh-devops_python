from web_admin import api_settings, setup_logger
import logging

logger = logging.getLogger(__name__)

class CustomerAPIService():
    def get_classification(self, classification_id):
        body = {}
        if classification_id:
            body['id'] = classification_id
        data, success = self._post_method(api_path=api_settings.GET_CUSTOMER_CLASSIFICATION_URL,
                                          func_description="Get customer classification",
                                          logger=logger,
                                          params=body)
        return data['classifications']


    def get_mm_card_type(self, mm_card_type_id):
        body = {}
        if mm_card_type_id:
            body['id'] = mm_card_type_id
        data, success = self._post_method(api_path=api_settings.GET_CUSTOMER_MM_CARD_TYPE_URL,
                                          func_description="Get customer mm card type",
                                          logger=logger,
                                          params=body)
        return data


    def get_mm_card_level(self, mm_card_type_level_id):
        body = {}
        if mm_card_type_level_id:
            body['id'] = mm_card_type_level_id
        data, success = self._post_method(api_path=api_settings.GET_CUSTOMER_MM_CARD_LEVEL_URL,
                                          func_description="Get customer mm card type levels",
                                          logger=logger,
                                          params=body)
        return data


    def get_kyc_level(self, kyc_level_id):
        body = {}
        if kyc_level_id:
            body['id'] = kyc_level_id
        data, success = self._post_method(api_path=api_settings.GET_CUSTOMER_KYC_LEVEL_URL,
                                          func_description="Get customer kyc level",
                                          logger=logger,
                                          params=body)
        return data