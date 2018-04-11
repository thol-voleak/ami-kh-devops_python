from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

import base64
import datetime
import logging
import urllib


def build_auth_header_from_request(request):
    return build_auth_header(settings.CLIENTID,
                             settings.CLIENTSECRET,
                             request.session.get('correlation_id'),
                             request.session.get('access_token'))


def build_auth_header(client_id, client_secret, correlation_id, access_token):
    headers = {
        'content-type': 'application/json',
        'correlation-id': correlation_id,
        'client_id': client_id,
        'client_secret': client_secret,
        'Authorization': 'Bearer {}'.format(access_token),
    }
    return headers


def build_logger(request, name):
    client_ip = get_client_ip(request)
    correlation_id = request.session.get('correlation_id')

    logger = logging.getLogger(name)

    return logging.LoggerAdapter(logger, extra={'IPAddress': client_ip, 'correlationId': correlation_id})


def get_client_ip(request):
    if request is not None:
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR')
    else:
        client_ip = ''

    return client_ip


def has_any_permission(request, args):
    permissions = request.session.get('permissions', [])
    for permission in args:
        if permission in [x['name'] for x in permissions]:
            return True
    return False


def encode_current_url_for_back(request):
    path = request.get_full_path()
    path = str.encode(path)
    path = base64.b64encode(path)
    path = urllib.parse.quote_plus(path)
    return path


def get_back_url(request, default_url=None):
    back_url = request.GET.get('back_url')

    if not back_url:
        return default_url

    path = urllib.parse.unquote_plus(back_url)
    path = base64.b64decode(path)
    path = path.decode()
    return path


def format_date_time(data):
    for item in data:
        if (item.get('created_timestamp') is not None) and (item['created_timestamp'] != "null"):
            created_at = item['created_timestamp'] / 1000.0
            item['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')

        if (item.get('last_updated_timestamp') is not None) and (
                    item['last_updated_timestamp'] != "null"):
            created_at = item['last_updated_timestamp'] / 1000.0
            item['last_updated_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')
    return data


def encrypt_text(input_text):
    utf8_text = input_text.encode('utf-8')
    pub_key = RSA.importKey(open(settings.RSA).read())
    cipher = PKCS1_v1_5.new(pub_key)
    cipher_text = base64.encodebytes(cipher.encrypt(utf8_text))
    return cipher_text.decode('utf-8')


def encrypt_text_agent(input_text):
    utf8_text = input_text.encode('utf-8')
    pub_key = RSA.importKey(open(settings.RSA_AGENT).read())
    cipher = PKCS1_v1_5.new(pub_key)
    cipher_text = base64.encodebytes(cipher.encrypt(utf8_text))
    return cipher_text.decode('utf-8')


def setup_logger(request, logger, correlation_id):
    if request is not None:
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR')
    else:
        client_ip = ''

    return logging.LoggerAdapter(logger, extra={'IPAddress': client_ip, 'correlationId': correlation_id})


def calculate_page_range_from_page_info(pageInfo):
    totalPages = pageInfo.get('total_pages')
    currentPage = pageInfo.get('current_page')
    pageRangeStart = 1
    pageRangeStop = totalPages + 1

    if totalPages > 6:
        if currentPage > 1:
            if currentPage == 3:
                pageRangeStart = 1
            elif currentPage < totalPages:
                pageRangeStart = currentPage - 1
            else:
                pageRangeStart = currentPage - 2
        if currentPage < totalPages:
            if currentPage == totalPages - 2:
                pageRangeStop = totalPages + 1
            elif currentPage > 1:
                pageRangeStop = currentPage + 2
            else:
                pageRangeStop = currentPage + 3
    pageRange = range(pageRangeStart, pageRangeStop)
    return pageRange
