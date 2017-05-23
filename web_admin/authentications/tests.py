from django.test import TestCase, Client
from . import apps
# from django.contrib.auth.models import User
# import unittest

# Create your tests here.
class AuthenticationTests(TestCase): # or unittest.TestCase

    def test_authentication_form_request_status_code(self):
        client = Client()
        response = self.client.get('/admin-portal')
        self.assertEqual(response.status_code, 301)

    def test_authentication_form_request_redirection(self):
        client = Client()
        response = self.client.get('/admin-portal/')
        self.assertRedirects(response, '/admin-portal/login/?next=/admin-portal/')

    def test_authentication_form_validation_successfully(self):
        username = 'admin'
        password = 'abcxyz'
        try:
            backend = apps.CustomBackend()
            backend._validateLoginForm(username, password)
        except apps.InvalidUsernamePassword:
            self.assertEqual(1, 0)
        else:
            self.assertEqual(1, 1)

    def test_authentication_form_validation_failed(self):
        username = 'admin'
        password = ''
        try:
            backend = apps.CustomBackend()
            backend._validateLoginForm(username, password)
        except apps.InvalidUsernamePassword:
            self.assertEqual(1, 1)
        else:
            self.assertEqual(1, 0)


    def test_authentication_wrong_username_password(self):
        username = 'Any_abcxyz'
        password = 'Any_pass_xyz'

        backend = apps.CustomBackend()
        result = backend.authenticate(username=username, password=password)

        self.assertEqual(result, None)

    """
    def test_authentication_correct_username_password(self):
        username = 'admin'
        password = 'pass99word'

        backend = apps.CustomBackend()
        result = backend.authenticate(username=username, password=password)

        self.assertNotEqual(result, None)
    """
