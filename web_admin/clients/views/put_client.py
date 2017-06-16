import time
import requests
from django.http import JsonResponse
from authentications.utils import get_auth_header
from django.conf import settings
from django.contrib import messages

def put_client(request, url, title, logger, client_id):
    logger.info('========== Start {} client =========='.format(title))
    params = {
        'status': title,
    }

    logger.info('API-Path: {}'.format(url))
    logger.info("Params: {} ".format(params))
    start = time.time()
    response = requests.put(url, headers=get_auth_header(request.user),
                            json=params, verify=settings.CERT)
    finish = time.time()
    logger.info('Response_code: {}'.format(response.status_code))
    logger.info('Response_content: {}'.format(response.text))
    logger.info('Response_time: {}'.format(finish - start))

    response_json = response.json()
    status = response_json.get('status', {})
    code = status.get('code', '')

    ajax_code = 0
    message = status.get('message', 'Something went wrong.')
    if code in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
        logger.info("{} for {} username".format(message, request.user))
        messages.add_message(request, messages.INFO, str('session_is_expired'))
        ajax_code = 1
        return JsonResponse({"status": ajax_code, "msg": message})

    if status['code'] == "success":
        ajax_code = 2
    else:
        ajax_code = 3
        logger.info('========== Finish {} client =========='.format(title))

    return JsonResponse({"status": ajax_code, "msg": message})