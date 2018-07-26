from web_admin import api_settings, setup_logger
from web_admin.api_logger import API_Logger
from web_admin import RestFulClient
import logging

logger = logging.getLogger(__name__)

class CustomerAPIService():

    def get_classification(self, classification_id):
        body = {}
        if classification_id:
            body['id'] = classification_id

        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_CUSTOMER_CLASSIFICATION_URL,
                                                                        headers=self._get_headers(),
                                                                        params=body,
                                                                        loggers=self.logger)
        API_Logger.post_logging(loggers=self.logger,
                                params=body,
                                response=data,
                                status_code=status_code,
                                is_getting_list=True)

        if success:
            data = data['classifications']
        else:
            data = {}
        return data

    def get_mm_card_type(self, mm_card_type_id):
        body = {}
        if mm_card_type_id:
            body['id'] = mm_card_type_id

        success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.GET_CUSTOMER_MM_CARD_TYPE_URL,
            headers=self._get_headers(),
            params=body,
            loggers=self.logger)
        API_Logger.post_logging(loggers=self.logger,
                                params=body,
                                response=data,
                                status_code=status_code,
                                is_getting_list=True)

        return data

    def get_mm_card_level(self, mm_card_type_level_id):
        body = {}
        if mm_card_type_level_id:
            body['id'] = mm_card_type_level_id

        success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.GET_CUSTOMER_MM_CARD_LEVEL_URL,
            headers=self._get_headers(),
            params=body,
            loggers=self.logger)
        API_Logger.post_logging(loggers=self.logger,
                                params=body,
                                response=data,
                                status_code=status_code,
                                is_getting_list=True)

        return data

    def get_kyc_level(self, kyc_level_id):
        body = {}
        if kyc_level_id:
            body['id'] = kyc_level_id

        success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.GET_CUSTOMER_KYC_LEVEL_URL,
            headers=self._get_headers(),
            params=body,
            loggers=self.logger)
        API_Logger.post_logging(loggers=self.logger,
                                params=body,
                                response=data,
                                status_code=status_code,
                                is_getting_list=True)

        return data