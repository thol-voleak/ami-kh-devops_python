import time
import requests
import json
from decimal import Decimal

from django.conf import settings
from web_admin.utils import setup_logger
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken


class RESTfulMethods(GetHeaderMixin):
    def _get_method(self, api_path, func_description, logger, is_getting_list=False, params={}):
        """
        :param api_path: 
        :param func_description: 
        :param logger: 
        :param is_getting_list: 
        :param params: 
        :return: 
        """

        if 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path
        logger = setup_logger(self.request, logger)
        logger.info('API-Path: {path}'.format(path=url))
        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        done = time.time()

        try:
            response_json = response.json()
            status = response_json.get('status', {})
            code = status.get('code', '')
        except Exception as e:
            logger.error(e)
            raise Exception(response.content)

        if response.status_code == 200 and code == "success":
            if is_getting_list:
                default_data = []
            else:
                default_data = {}
            data = response_json.get('data', default_data)

            if len(params) > 0:
                logger.info("Params: {} ".format(params))
            logger.info('Response_code: {}'.format(response.status_code))
            if is_getting_list:
                logger.info('Response_content_count: {}'.format(len(data)))
            else:
                logger.info('Response_content: {}'.format(response.text))
            logger.info('Response_time: {}'.format(done - start_date))

            result = data, True
        else:
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result

    def _put_method(self, api_path, func_description, logger, params={}):
        """
        :param api_path: the API path
        :param func_description: the description of method, used for logging
        :param logger: the logger object to print log
        :param params: the data of put method
        :return: data and success (True or False)
        """

        if 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path
        logger = setup_logger(self.request, logger)
        logger.info('API-Path: {path}'.format(path=api_path))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(), json=params, verify=settings.CERT)
        done = time.time()

        # Filter sensitive data
        self._filter_sensitive_fields(params=params)
        logger.info("Params: {} ".format(params))
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.text))
        logger.info('Response_time: {}'.format(done - start_date))

        try:
            response_json = response.json()
            status = response_json.get('status', {})
            code = status.get('code', '')
        except Exception as e:
            logger.error(e)

        if code == "success":
            result = response_json.get('data', {}), True
        else:
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result

    def _post_method(self, api_path, func_description, logger, params={}, only_return_data=True):
        """
        :param api_path: 
        :param func_description: 
        :param logger: 
        :param params: 
        :return: 
        """

        if 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path
        logger = setup_logger(self.request, logger)
        logger.info('API-Path: {path}'.format(path=api_path))

        start_time = time.time()
        response = requests.post(url, headers=self._get_headers(), json=params, verify=settings.CERT)
        end_time = time.time()

        # Filter sensitive data
        self._filter_sensitive_fields(params=params)

        logger.info("Params: {} ".format(params))
        logger.info("Response_code: {}".format(response.status_code))

        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')
        logger.info("Response_time: {}".format(end_time - start_time))
        if code == "success":
            data = response_json.get('data', {})
            if isinstance(data, list):
                logger.info("Response_content_count: {}".format(len(data)))
            else:
                logger.info("Response_content: {}".format(response.content))
            if only_return_data:
                result = data, True
            else:
                result = response_json, True
        else:
            logger.info("Response_content: {}".format(response.text))
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result

    def _delete_method(self, api_path, func_description, logger, params={}):

        if 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path
        logger = setup_logger(self.request, logger)
        logger.info('API-Path: {path}'.format(path=api_path))

        start_time = time.time()
        response = requests.delete(url, headers=self._get_headers(), json=params, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {}".format(end_time - start_time))

        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')

        if code == "success":
            result = response_json.get('data', {}), True
        else:
            result = {}, False
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                raise InvalidAccessToken(message)
            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result
    
    def _get_precision_method(self, api_path, func_description, logger, is_getting_list=False, params={}):
        """
        :param api_path: 
        :param func_description: 
        :param logger: 
        :param is_getting_list: 
        :param params: 
        :return: 
        """

        if 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path
        logger = setup_logger(self.request, logger)
        logger.info('API-Path: {path}'.format(path=url))
        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        done = time.time()

        try:
            response_json = json.loads(response.text, parse_float=Decimal)
            status = response_json.get('status', {})
            code = status.get('code', '')
        except Exception as e:
            logger.error(e)
            raise Exception(response.content)

        if response.status_code == 200 and code == "success":
            if is_getting_list:
                default_data = []
            else:
                default_data = {}
            data = response_json.get('data', default_data)

            if len(params) > 0:
                logger.info("Params: {} ".format(params))
            logger.info('Response_code: {}'.format(response.status_code))
            if is_getting_list:
                logger.info('Response_content_count: {}'.format(len(data)))
            else:
                logger.info('Response_content: {}'.format(response.text))
            logger.info('Response_time: {}'.format(done - start_date))

            result = data, True
        else:
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result

    '''
    Author: Steve Le
    History:
    # 2017-05-18: Init
    - For skip sensitive fields for logging data.
    '''

    @staticmethod
    def _filter_sensitive_fields(params={}):

        if 'password' in params:
            params['password'] = '******'

        if 're-password' in params:
            params['re-password'] = '******'

        return params;
