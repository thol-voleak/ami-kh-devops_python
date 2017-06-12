import datetime
from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

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

def encryptText(input):
    utf8_text = input.encode('utf-8')
    pub_key = RSA.importKey(open(settings.RSA).read())
    cipher = PKCS1_v1_5.new(pub_key)
    ciphertext = base64.encodebytes(cipher.encrypt(utf8_text))
    return ciphertext.decode('utf-8')

def encryptText_agent(input):
    utf8_text = input.encode('utf-8')
    pub_key = RSA.importKey(open(settings.RSA_AGENT).read())
    cipher = PKCS1_v1_5.new(pub_key)
    ciphertext = base64.encodebytes(cipher.encrypt(utf8_text))
    return ciphertext.decode('utf-8')
