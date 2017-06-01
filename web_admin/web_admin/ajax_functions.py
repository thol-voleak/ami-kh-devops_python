import time
import requests
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from authentications.utils import get_auth_header

def _delete_method(request, api_path, func_description, logger, params=None):
    if 'https' not in api_path:
        url = settings.DOMAIN_NAMES + api_path
    else:
        url = api_path
    logger.info('API-Path: {path}'.format(path=api_path))
    start = time.time()
    response = requests.delete(url, headers=get_auth_header(request.user), json=params, verify=settings.CERT)
    done = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(done - start))
    response_json = response.json()
    status = response_json.get('status', {})

    code = 0
    message = status.get('message', 'Something went wrong.')
    if status['code'] in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('session_is_expired'))
        code = 1
        return JsonResponse({"status": code, "msg": message})

    if status['code'] == "success":
        code = 2
    else:
        code = 3

    return JsonResponse({"status": code, "msg": message})

def _post_method(request, api_path, func_description, logger, params={}):
    if 'https' not in api_path:
        url = settings.DOMAIN_NAMES + api_path
    else:
        url = api_path
    logger.info('API-Path: {path}'.format(path=api_path))

    start = time.time()
    response = requests.post(url, headers=get_auth_header(request.user), json=params, verify=settings.CERT)
    done = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(done - start))
    response_json = response.json()
    status = response_json.get('status', {})

    code = 0
    message = status.get('message', 'Something went wrong.')
    if status['code'] in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('session_is_expired'))
        code = 1
        return JsonResponse({"status": code, "msg": message})

    if status['code'] == "success":
        code = 2
    else:
        code = 3

    return JsonResponse({"status": code, "msg": message})

def _put_method(request, api_path, func_description, logger, params={}):
    if 'https' not in api_path:
        url = settings.DOMAIN_NAMES + api_path
    else:
        url = api_path
    logger.info('API-Path: {path}'.format(path=api_path))
    logger.info("Params: {} ".format(params))

    start = time.time()
    response = requests.put(url, headers=get_auth_header(request.user), json=params, verify=settings.CERT)
    done = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(done - start))
    response_json = response.json()
    status = response_json.get('status', {})

    code = 0
    message = status.get('message', 'Something went wrong.')
    if status['code'] in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('session_is_expired'))
        code = 1
        return JsonResponse({"status": code, "msg": message})

    if status['code'] == "success":
        code = 2
    else:
        code = 3

    return JsonResponse({"status": code, "msg": message})

