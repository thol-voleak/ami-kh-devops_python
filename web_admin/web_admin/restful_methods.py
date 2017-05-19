import time
import requests

from django.conf import settings
from django.shortcuts import redirect

from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken

class RESTfulMethods(GetHeaderMixin):
    def _get_method(self, api_path, func_description, logger, is_getting_list = False, params = {}):
        """
        :param api_path: 
        :param func_description: 
        :param logger: 
        :param is_getting_list: 
        :param params: 
        :return: 
        """
        logger.info('========== Start getting {func_description} =========='.format(func_description=func_description))

        if 'https' in api_path or 'http' in api_path:
            url = api_path
        else:
            url = settings.DOMAIN_NAMES + api_path
        logger.info('API-Path: {path}'.format(path=url))

        start_date = time.time()
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        done = time.time()
        logger.info("response === {}".format(response.content))
        response_json = response.json()

        status = response_json.get('status', {})

        code = status.get('code', '')

        if is_getting_list:
            default_data = []
        else:
            default_data = {}

        if response.status_code == 200 and code == "success":
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
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
            result = default_data, False
            raise Exception(response.content)
        logger.info('========== Finished getting {func_description} =========='.format(func_description=func_description))
        return result

    def _put_method(self, api_path, func_description, logger, params={}):
        """
        :param api_path: the API path
        :param func_description: the description of method, used for logging
        :param logger: the logger object to print log
        :param params: the data of put method
        :return: data and success (True or False)
        """
        logger.info('========== Start updating {func_description} =========='.format(func_description=func_description))

        if 'https' not in api_path:
            url = settings.DOMAIN_NAMES + api_path
        else:
            url = api_path
        logger.info('API-Path: {path}'.format(path=api_path))
        logger.info("Params: {} ".format(params))

        start_date = time.time()
        response = requests.put(url, headers=self._get_headers(),
                                json=params, verify=settings.CERT)
        done = time.time()

        response_json = response.json()
        status = response_json.get('status', {})

        code = status.get('code', '')
        if code == "success":
            logger.info('Response_code: {}'.format(response.status_code))
            logger.info('Response_content: {}'.format(response.text))
            logger.info('Response_time: {}'.format(done - start_date))

            result = response_json.get('data', {}), True
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            result = None, False
        logger.info('========== Finished updating {} =========='.format(func_description))
        return result

    def _post_method(self, api_path, func_description, logger, params={}):
        """
        :param api_path: 
        :param func_description: 
        :param logger: 
        :param params: 
        :return: 
        """
        logger.info('========== Start creating {func_description} =========='.format(func_description=func_description))

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
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {}".format(end_time - start_time))

        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')

        if code == "success":
            result = response_json.get('data', {}), True
        else:
            result = {}, False
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
        logger.info('========== Finished creating {} =========='.format(func_description))
        return result

    def _delete_method(self, api_path, func_description, logger):
        logger.info('========== Start deleting {func_description} =========='.format(func_description=func_description))

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
        response = requests.delete(url, headers=self._get_headers(), verify=settings.CERT)
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
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
        logger.info('========== Finished deleting {} =========='.format(func_description))
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
    def _filter_sensitive_fields(params = {}):

        if 'password' in params:
            params['password'] = None

        if 're-password' in params:
            params['re-password'] = None

        return params;