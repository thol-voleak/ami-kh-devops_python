from django.test import TestCase, Client
from . import views
from authentications import apps
from django.conf import settings
import requests, json, random, string, logging, datetime
from authentications.models import Authentications

# from django.contrib.auth.models import User
# import unittest

# Hardcoded here for testing. Because system user is given logged in:
access_token = '9233f143-cde8-40f2-b304-9a23fc39160a'


# Create your tests here.
class ClientCredentialsTests(TestCase):  # or unittest.TestCase

    def test_client_credentials_request_status_code(self):
        client = Client()
        response = client.get('/admin-portal/client-credentials')
        self.assertEqual(response.status_code, 302)

    def test_client_credentials_get_list_clients(self):

        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.CLIENTS_LIST_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        payload = {}
        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer ' + access_token
        }

        auth_request = requests.get(url, params=payload, headers=headers)
        json_data = auth_request.json()
        data = json_data.get('data')

        if (data is not None) and (len(data) > 0):
            self.assertEqual(1, 1)
        else:
            self.assertEqual(1, 0)

    def test_client_credentials_created_at_updated_at_right_format(self):

        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.CLIENTS_LIST_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        payload = {}
        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer ' + access_token
        }

        auth_request = requests.get(url, params=payload, headers=headers)
        json_data = auth_request.json()
        data = json_data.get('data')

        if (data is not None) and (len(data) > 0):
            refined_data = views.ListView()._refine_data(data)
            for client in refined_data:
                # Check Format of Creation Date
                if (client['created_timestamp'] is not None) and (client['created_timestamp'] != "null"):
                    try:
                        s = client['created_timestamp']
                        datetime.datetime.strptime(s, '%d-%m-%Y %H:%M').date()
                    except:
                        self.assertEqual(3, 0)

                # Check Format of Modification Date
                if (client['last_updated_timestamp'] is not None) and (client['last_updated_timestamp'] != "null"):
                    try:
                        s = client['last_updated_timestamp']
                        datetime.datetime.strptime(s, '%d-%m-%Y %H:%M').date()
                    except:
                        self.assertEqual(4, 0)

            self.assertEqual(1, 1)
        else:
            self.assertEqual(2, 0)

    def test_client_credentials_clients_id_required(self):

        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.CLIENTS_LIST_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        payload = {}
        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer ' + access_token,
            # 'Authorization': 'Bearer ' + access_token,
        }

        auth_request = requests.get(url, params=payload, headers=headers)
        json_data = auth_request.json()
        data = json_data.get('data')

        if (data is not None) and (len(data) > 0):
            refined_data = views.ListView()._refine_data(data)
            for client in refined_data:
                # Check Format of Creation Date
                if (client['client_id'] is None) or (client['client_id'] == "null"):
                    self.assertEqual(1, 0)

            self.assertEqual(1, 1)
        else:
            self.assertEqual(2, 0)

    def test_client_credentials_created_at_less_than_updated_at(self):

        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.CLIENTS_LIST_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        payload = {}
        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer ' + access_token,
        }

        auth_request = requests.get(url, params=payload, headers=headers)
        json_data = auth_request.json()
        data = json_data.get('data')

        if (data is not None) and (len(data) > 0):
            for client in data:
                if (client['created_timestamp'] is not None) and (client['created_timestamp'] != "null") and (
                            client['last_updated_timestamp'] is not None) and (
                            client['last_updated_timestamp'] != "null"):
                    if float(client['created_timestamp']) > float(client['last_updated_timestamp']):
                        self.assertEqual(1, 0)

            self.assertEqual(1, 1)
        else:
            self.assertEqual(2, 0)
