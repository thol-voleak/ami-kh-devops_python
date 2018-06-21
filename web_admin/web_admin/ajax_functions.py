import time
import requests
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from authentications.utils import get_auth_header


def _delete_method(request, api_path, func_description, logger, params=None, timeout=None):
    if 'http' in api_path:
        url = api_path
    else:
        url = settings.DOMAIN_NAMES + api_path

    if timeout is None:
        timeout = settings.GLOBAL_TIMEOUT

    logger.info('API-Path: {path}'.format(path=api_path))
    start = time.time()
    try:
        response = requests.delete(url, headers=get_auth_header(request.user), json=params, verify=settings.CERT,
                                   timeout=timeout)
    except requests.exceptions.Timeout:
        done = time.time()
        logger.info('Request timeout')
        logger.info('Response_time: {}'.format(done - start))
        return JsonResponse({'status': 'timeout', "msg": "timeout"})

    done = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(done - start))
    response_json = response.json()
    status = response_json.get('status', {})

    code = 0
    message = status.get('message', 'Something went wrong.')
    if status['code'] in ['access_token_expire', 'authentication_fail', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('Your login credentials have expired. Please login again.'))
        code = 1
        return JsonResponse({"status": code, "msg": message})

    if status['code'] == "success":
        code = 2
    else:
        code = 3

    return JsonResponse({"status": code, "msg": message})


def _post_method(request, api_path, func_description, logger, params={}, timeout=None):
    if 'http' in api_path:
        url = api_path
    else:
        url = settings.DOMAIN_NAMES + api_path

    if timeout is None:
        timeout = settings.GLOBAL_TIMEOUT

    logger.info('API-Path: {path}'.format(path=api_path))

    start = time.time()
    try:
        response = requests.post(url, headers=get_auth_header(request.user), json=params, verify=settings.CERT,
                                 timeout=timeout)
    except requests.exceptions.Timeout:
        return JsonResponse({'status': 'timeout'})
    done = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(done - start))
    response_json = response.json()
    status = response_json.get('status', {})

    code = 0
    message = status.get('message', 'Something went wrong.')
    if status['code'] in ['access_token_expire', 'authentication_fail', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('Your login credentials have expired. Please login again.'))
        code = 1
        return JsonResponse({"status": code, "msg": message})

    if status['code'] == "success":
        code = 2
    else:
        code = 3

    return JsonResponse({"status": code, "msg": message, "data": response_json.get('data', {})})

def _post_method_return_error_if_error(request, api_path, func_description, logger, params={}, timeout=None):
    if 'http' in api_path:
        url = api_path
    else:
        url = settings.DOMAIN_NAMES + api_path

    if timeout is None:
        timeout = settings.GLOBAL_TIMEOUT

    logger.info('API-Path: {path}'.format(path=api_path))

    start = time.time()
    try:
        response = requests.post(url, headers=get_auth_header(request.user), json=params, verify=settings.CERT,
                                 timeout=timeout)
    except requests.exceptions.Timeout:
        return JsonResponse({'status': 'timeout'})
    done = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(done - start))
    response_json = response.json()
    status = response_json.get('status', {})

    code = 0
    message = status.get('message', 'Something went wrong.')
    if status['code'] in ['access_token_expire', 'authentication_fail', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('Your login credentials have expired. Please login again.'))
        code = 1
        return JsonResponse({"status": code, "msg": message})

    if status['code'] == "success":
        code = 2
    else:
        code = 3

    if response.status_code == 400:
        return JsonResponse({'status': 'false', 'message': message}, status=400)
    return JsonResponse({"status": code, "msg": message, "data": response_json.get('data', {})})

def _put_method(request, api_path, func_description, logger, params={}, timeout=None):
    if 'http' in api_path:
        url = api_path
    else:
        url = settings.DOMAIN_NAMES + api_path

    if timeout is None:
        timeout = timeout

    logger.info('API-Path: {path}'.format(path=api_path))
    logger.info("Params: {} ".format(params))

    start = time.time()
    try:
        response = requests.put(url, headers=get_auth_header(request.user), json=params, verify=settings.CERT,
                                timeout=timeout)
    except requests.exceptions.Timeout:
        return JsonResponse({'status': 'timeout'})

    done = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(done - start))
    response_json = response.json()
    status = response_json.get('status', {})

    code = 0
    message = status.get('message', 'Something went wrong.')
    if status['code'] in ['access_token_expire', 'authentication_fail', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('Your login credentials have expired. Please login again.'))
        code = 1
        return JsonResponse({"status": code, "msg": message})

    if status['code'] == "success":
        code = 2
    else:
        code = 3

    server_error_code = ''
    if response.status_code:
        server_error_code = response.status_code

    return JsonResponse({"status": code, "msg": message, 'server_error_code': server_error_code})
