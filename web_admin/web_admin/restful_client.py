from django.conf import settings

import time
import requests

from .utils import setup_logger

class RestFulClient:
    @classmethod
    def get(cls, request, url, headers, logger):
        if 'http' not in url:
            url = settings.DOMAIN_NAMES + url

        logger = setup_logger(request, logger)

        start_time = time.time()
        response = requests.get(url, headers = headers, verify = settings.CERT)
        end_time = time.time()
        processing_time = end_time - start_time

        http_status_code = response.status_code
        logger.info('Get {path} result with [{http_status_code}] HTTP status code. Processing time: [{processing_time}]'
                    .format(path = url, http_status_code = http_status_code, processing_time = processing_time))
        try:
            response_json = response.json()
            status = response_json.get('status', {})
            status_code = status.get('code', '')
            status_message = status.get('message', '')
            logger.info('Status code: [{status_code}]. Status message: [{status_message}]'
                    .format(status_code = status_code, status_message = status_message))

            data = response_json.get('data', '')

            is_success = (http_status_code == 200) and (status_code == "success")
        except Exception as e:
            logger.error(e)
            raise Exception(response.content)

        return is_success, status_code, data

    @classmethod
    def post(cls, request, url, headers, logger, params={}):
        if 'http' not in url:
            url = settings.DOMAIN_NAMES + url

        logger = setup_logger(request, logger)

        start_time = time.time()
        response = requests.post(url, headers=headers, json=params, verify=settings.CERT)
        end_time = time.time()
        processing_time = end_time - start_time

        http_status_code = response.status_code
        logger.info('Get {path} result with {http_status_code} HTTP status code. Processing time: [{processing_time}]'
                    .format(path = url, http_status_code = http_status_code, processing_time = processing_time))
        try:
            response_json = response.json()
            status = response_json.get('status', {})
            status_code = status.get('code', '')
            status_message = status.get('message', '')
            logger.info('Status code: [{status_code}]. Status message: [{status_message}]'
                    .format(status_code = status_code, status_message = status_message))

            data = response_json.get('data', '')

            is_success = (http_status_code == 200) and (status_code == "success")
        except Exception as e:
            logger.error(e)
            raise Exception(response.content)

        return is_success, status_code, status_message, data
