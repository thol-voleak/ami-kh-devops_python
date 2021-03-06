import time
import requests
import json
from decimal import Decimal

from django.conf import settings
from web_admin.utils import setup_logger
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken


class RESTfulReconcileMethods(GetHeaderMixin):
    def _get_method(self, api_path, func_description=None, logger=None, is_getting_list=False, params={}):
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

        self.logger.info('API-Path: {path}'.format(path=url))
        start_time = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        end_time = time.time()

        self.logger.info("Response_code: {}".format(response.status_code))
        self.logger.info("Response_time: {}".format(end_time - start_time))

        response_json = response.json()
        response_json['status_code'] = response.status_code

        if response.status_code == 500:
            self.logger.info("Response: {}".format(response_json))
            result = response_json, False
        else:
            try:
                status = response_json.get('status', {})
                code = status.get('code', '')
            except Exception as e:
                self.logger.error(e)
                raise Exception(response.content)

            if response.status_code == 200 and code == "success":
                if is_getting_list:
                    default_data = []
                else:
                    default_data = {}
                data = response_json.get('data', default_data)

                if len(params) > 0:
                    self.logger.info("Params: {} ".format(params))

                self.logger.info('Response_code: {}'.format(response.status_code))
                if is_getting_list:
                    self.logger.info('Response_content_count: {}'.format(len(data)))
                else:
                    self.logger.info('Response_content: {}'.format(response.text))
                self.logger.info('Response_time: {}'.format(end_time - start_time))

                result = data, True
            else:
                message = status.get('message', '')
                if (code == "access_token_expire") or (code == 'authentication_fail') or (
                            code == 'invalid_access_token'):
                    self.logger.info("{} for {} username".format(message, self.request.user))
                    raise InvalidAccessToken(message)
                if message:
                    result = message, False
                else:
                    raise Exception(response.content)

        return result

    def _put_method(self, api_path, func_description, logger=None, params={}):
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

        self.logger.info('API-Path: {path}'.format(path=api_path))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(), json=params, verify=settings.CERT)
        done = time.time()

        # Filter sensitive data
        self._filter_sensitive_fields(params=params)
        self.logger.info("Params: {} ".format(params))
        self.logger.info('Response_code: {}'.format(response.status_code))
        self.logger.info('Response_content: {}'.format(response.text))
        self.logger.info('Response_time: {}'.format(done - start_date))

        try:
            response_json = response.json()
            status = response_json.get('status', {})
            code = status.get('code', '')
        except Exception as e:
            self.logger.error(e)
            raise Exception(response.content)

        if code == "success":
            result = response_json.get('data', {}), True
        else:
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'authentication_fail') or (
                        code == 'invalid_access_token'):
                self.logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result

    def _post_method(self, api_path, func_description=None, logger=None, params={}, only_return_data=True):
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

        self.logger.info('API-Path: {path}'.format(path=api_path))

        start_time = time.time()
        response = requests.post(url, headers=self._get_headers(), json=params, verify=settings.CERT)
        end_time = time.time()

        # Filter sensitive data
        self._filter_sensitive_fields(params=params)

        self.logger.info("Params: {} ".format(params))
        self.logger.info("Response_code: {}".format(response.status_code))

        response_json = response.json()

        self.logger.info("Response_time: {}".format(end_time - start_time))
        response_json['status_code'] = response.status_code

        if response.status_code == 500:
            self.logger.info("Response: {}".format(response_json))
            result = response_json, False
        else:
            status = response_json.get('status', {})
            code = status.get('code', '')
            if code == "success":
                data = response_json.get('data', {})
                if isinstance(data, list):
                    self.logger.info("Response_content_count: {}".format(len(data)))
                else:
                    self.logger.info("Response_content: {}".format(response.content))
                if only_return_data:
                    result = data, True
                else:
                    result = response_json, True
            else:
                self.logger.info("Response_content: {}".format(response.text))
                message = status.get('message', '')
                if (code == "access_token_expire") or (code == 'authentication_fail') or (
                            code == 'invalid_access_token'):
                    self.logger.info("{} for {} username".format(message, self.request.user))
                    raise InvalidAccessToken(message)

                if message:
                    result = message, False
                else:
                    raise Exception(response.content)
        return result

    def _delete_method(self, api_path, func_description, logger=None, params={}):

        if 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path

        self.logger.info('API-Path: {path}'.format(path=api_path))

        start_time = time.time()
        response = requests.delete(url, headers=self._get_headers(), json=params, verify=settings.CERT)
        end_time = time.time()

        self.logger.info("Response_code: {}".format(response.status_code))
        self.logger.info("Response_content: {}".format(response.content))
        self.logger.info("Response_time: {}".format(end_time - start_time))

        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')

        if code == "success":
            result = response_json.get('data', {}), True
        else:
            result = {}, False
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'authentication_fail') or (
                        code == 'invalid_access_token'):
                raise InvalidAccessToken(message)
            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result
    
    def _get_precision_method(self, api_path, func_description, logger=None, is_getting_list=False, params={}):
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

        self.logger.info('API-Path: {path}'.format(path=url))
        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        done = time.time()

        try:
            response_json = json.loads(response.text, parse_float=Decimal)
            status = response_json.get('status', {})
            code = status.get('code', '')
        except Exception as e:
            self.logger.error(e)
            raise Exception(response.content)

        if response.status_code == 200 and code == "success":
            if is_getting_list:
                default_data = []
            else:
                default_data = {}
            data = response_json.get('data', default_data)

            if len(params) > 0:
                self.logger.info("Params: {} ".format(params))
            self.logger.info('Response_code: {}'.format(response.status_code))

            if is_getting_list:
                self.logger.info('Response_content_count: {}'.format(len(data)))
            else:
                self.logger.info('Response_content: {}'.format(response.text))
            self.logger.info('Response_time: {}'.format(done - start_date))

            result = data, True
        else:
            message = status.get('message', '')
            if (code == "access_token_expire") or (code == 'authentication_fail') or (
                        code == 'invalid_access_token'):
                self.logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            if message:
                result = message, False
            else:
                raise Exception(response.content)
        return result

    @staticmethod
    def _filter_sensitive_fields(params={}):

        if 'password' in params:
            params['password'] = '******'

        if 're-password' in params:
            params['re-password'] = '******'

        return params;
