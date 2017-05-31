import time
import requests

from django.conf import settings

from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken


class AjaxMethods(GetHeaderMixin):
    def _get_method(self, api_path, func_description, logger, is_getting_list=False, params={}, is_return_all=False):
        """
        :param api_path: 
        :param func_description: 
        :param logger: 
        :param is_getting_list: 
        :param params: 
        :return: 
        """

        if 'https' in api_path or 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path
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

        if response.status_code == 200 or code == "success":
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

            if not is_return_all:
                result = data, True
            else:
                result = response, True
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (code == 'invalid_access_token'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
            raise Exception(response.content)
        return result

    def _put_method(self, api_path, func_description, logger, params={}, is_return_all=False):
        """
        :param api_path: the API path
        :param func_description: the description of method, used for logging
        :param logger: the logger object to print log
        :param params: the data of put method
        :return: data and success (True or False)
        """

        if 'https' not in api_path:
            url = settings.DOMAIN_NAMES + api_path
        else:
            url = api_path
        logger.info('API-Path: {path}'.format(path=api_path))
        logger.info("Params: {} ".format(params))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(), json=params, verify=settings.CERT)
        done = time.time()
        try:
            response_json = response.json()
            status = response_json.get('status', {})
            code = status.get('code', '')
        except Exception as e:
            logger.error(e)

        if code == "success":
            logger.info('Response_code: {}'.format(response.status_code))
            logger.info('Response_content: {}'.format(response.text))
            logger.info('Response_time: {}'.format(done - start_date))

            data = response_json.get('data', {})

            if not is_return_all:
                result = data, True
            else:
                result = response, True
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                message = status.get('message', 'Something went wrong.')
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            raise Exception(response.content)
        return result

    def _post_method(self, api_path, func_description, logger, params={}, is_return_all=False):
        """
        :param api_path: 
        :param func_description: 
        :param logger: 
        :param params: 
        :return: 
        """

        if 'https' not in api_path:
            url = settings.DOMAIN_NAMES + api_path
        else:
            url = api_path
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

        if code == "success":
            data = response_json.get('data', {})
            if isinstance(data, list):
                logger.info("Response_content_count: {}".format(len(data)))
            else:
                logger.info("Response_content: {}".format(response.content))
            logger.info("Response_time: {}".format(end_time - start_time))
            if not is_return_all:
                result = data, True
            else:
                result = response, True
        else:
            logger.info("Response_content: {}".format(response.content))
            logger.info("Response_time: {}".format(end_time - start_time))
            message = status.get('message', 'Something went wrong.')

            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            result = {}, False
        return result

    def _delete_method(self, api_path, func_description, logger, params=None, is_return_all=False):

        if 'https' not in api_path:
            url = settings.DOMAIN_NAMES + api_path
        else:
            url = api_path
        logger.info('API-Path: {path}'.format(path=api_path))

        # url = settings.BALANCE_DISTRIBUTION_DETAIL_URL.format(
        #     balance_distribution_id=balance_distribution_id
        # )
        # logger.info("Delete balance distribution by user: {} with url: {}".format(
        #     self.request.user.username,
        #     url,
        # ))
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
            data = response_json.get('data', {})
            if not is_return_all:
                result = data, True
            else:
                result = response, True
        else:
            result = {}, False
            if (code == "access_token_expire") or (code == 'access_token_not_found') or (
                        code == 'invalid_access_token'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
        return result


        # logger.info("Response status: {}, reponse content: {}".format(
        #     response.status_code,
        #     response.content,
        # ))
        # if response.status_code == 200:
        #     return True
        # return False

    '''
    Author: Steve Le
    History:
    # 2017-05-18: Init
    - For skip sensitive fields for logging data.
    '''

    @staticmethod
    def _filter_sensitive_fields(params={}):

        if 'password' in params:
            params['password'] = None

        if 're-password' in params:
            params['re-password'] = None

        return params;
