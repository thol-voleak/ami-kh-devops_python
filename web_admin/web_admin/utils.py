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
