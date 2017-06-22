from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

import base64
import datetime
import logging


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


def setup_logger(request, logger):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        logger.info("Found HTTP_X_FORWARDED_FOR header with value [{}]".format(x_forwarded_for))
        client_ip = x_forwarded_for.split(',')[0].strip()
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    return logging.LoggerAdapter(logger, extra={'IPAddress': client_ip})
