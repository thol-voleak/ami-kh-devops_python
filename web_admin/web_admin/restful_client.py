from django.conf import settings

import logging
import requests
import time

logger = logging.getLogger(__name__)


class RestFulClient:
    @classmethod
    def get(cls, url, loggers, headers, timeout=None):
        if 'http' not in url:
            url = settings.DOMAIN_NAMES + url
        if timeout is None:
            timeout = settings.GLOBAL_TIMEOUT
        try:
            loggers.info('Get path: [{path}]'.format(path=url))
            start_time = time.time()
            response = requests.get(url, headers=headers, verify=settings.CERT, timeout=timeout)
            end_time = time.time()
            processing_time = end_time - start_time
            http_status_code = response.status_code
            loggers.info('Result is [{http_status_code}] HTTP status code.'.format(http_status_code=http_status_code))
            loggers.info('Processing time: [{processing_time}]'.format(processing_time=processing_time))
            try:
                response_json = response.json()
                status = response_json.get('status', {})
                status_code = status.get('code', '')
                status_message = status.get('message', '')
                loggers.info('Status code: [{status_code}].'.format(status_code=status_code))
                loggers.info('Status message: [{status_message}].'.format(status_message=status_message))

                data = response_json.get('data', '')
                is_success = (http_status_code == 200) and (status_code == "success")
            except Exception as e:
                loggers.error(e)
                raise Exception(response)
        except requests.exceptions.Timeout:
            is_success, status_code, data = False, 'Timeout', 'timeout'

        return is_success, status_code, data

    @classmethod
    def post(cls, url, headers, loggers, params={}, timeout=None):
        if 'http' not in url:
            url = settings.DOMAIN_NAMES + url
        if timeout is None:
            timeout = settings.GLOBAL_TIMEOUT
        try:
            loggers.info('Get path: [{path}]'.format(path=url))
            start_time = time.time()
            response = requests.post(url, headers=headers, json=params, verify=settings.CERT, timeout=timeout)
            end_time = time.time()
            processing_time = end_time - start_time
            http_status_code = response.status_code
            loggers.info('Result is [{http_status_code}] HTTP status code.'.format(http_status_code=http_status_code))
            loggers.info('Processing time: [{processing_time}]'.format(processing_time=processing_time))

            try:
                response_json = response.json()
                status = response_json.get('status', {})
                status_code = status.get('code', '')
                status_message = status.get('message', '')
                loggers.info('Status code: [{status_code}].'.format(status_code=status_code))
                loggers.info('Status message: [{status_message}].'.format(status_message=status_message))

                data = response_json.get('data', '')

                is_success = (http_status_code == 200) and (status_code == "success")
            except Exception as e:
                loggers.error(e)
                raise Exception(response)
        except requests.exceptions.Timeout:
            is_success, status_code, status_message, data = False, 'Timeout', 'timeout', None

        return is_success, status_code, status_message, data

    @classmethod
    def put(cls, url, headers, loggers, params={}, timeout=None):
        if 'http' not in url:
            url = settings.DOMAIN_NAMES + url
        if timeout is None:
            timeout = settings.GLOBAL_TIMEOUT
        try:
            start_time = time.time()
            response = requests.put(url, headers=headers, json=params, verify=settings.CERT, timeout=timeout)
            http_status_code = response.status_code
            end_time = time.time()
            processing_time = end_time - start_time
            loggers.info(
                'Get {path} result with {http_status_code} HTTP status code.'.format(path=url,
                                                                                     http_status_code=http_status_code))
            loggers.info('Processing time: [{processing_time}]'.format(processing_time=processing_time))
            try:
                response_json = response.json()
                status = response_json.get('status', {})
                status_code = status.get('code', '')
                status_message = status.get('message', '')
                loggers.info('Status code: [{status_code}].'.format(status_code=status_code))
                loggers.info('Status message: [{status_message}].'.format(status_message=status_message))

                data = response_json.get('data', '')
                is_success = (http_status_code == 200) and (status_code == "success")
            except Exception as e:
                loggers.error(e)
                raise Exception(response)
        except requests.exceptions.Timeout:
            is_success, status_code, status_message, data = False, 'Timeout', 'timeout', None

        return is_success, status_code, status_message, data

    @classmethod
    def delete(cls, url, headers, loggers, params={}, timeout=None):
        if 'http' not in url:
            url = settings.DOMAIN_NAMES + url
        if timeout is None:
            timeout = settings.GLOBAL_TIMEOUT

        try:
            start_time = time.time()
            response = requests.delete(url, headers=headers, json=params, verify=settings.CERT, timeout=timeout)
            end_time = time.time()
            processing_time = end_time - start_time
            http_status_code = response.status_code
            loggers.info(
                'Get {path} result with {http_status_code} HTTP status code.'.format(path=url,
                                                                                     http_status_code=http_status_code))
            loggers.info('Processing time: [{processing_time}]'.format(processing_time=processing_time))
            try:
                response_json = response.json()
                status = response_json.get('status', {})
                status_code = status.get('code', '')
                status_message = status.get('message', '')
                loggers.info('Status code: [{status_code}].'.format(status_code=status_code))
                loggers.info('Status message: [{status_message}].'.format(status_message=status_message))

                is_success = (http_status_code == 200) and (status_code == "success")
            except Exception as e:
                loggers.error(e)
                raise Exception(response)
        except requests.exceptions.Timeout:
            is_success, status_code, data = False, 'Timeout', 'timeout'

        return is_success, status_code, status_message
