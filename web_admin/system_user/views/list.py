from django.views.generic.base import TemplateView
from django.conf import settings

import requests
import random
import string
import time
import logging
import datetime

from authentications.models import *
from authentications.apps import InvalidAccessToken

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "system_user/system_user_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get system user List ==========')
        data = self.get_system_user_list()
        refined_data = _refine_data(data)
        logger.info('========== Finished get system user List ==========')
        result = {'data': refined_data,
                'created_msg': self.request.session.pop('system_user_create_msg', None),
                'del_msg': self.request.session.pop('system_user_delete_msg', None),
                'pw_msg': self.request.session.pop('system_user_change_password_msg', None)}
        return result

    def get_system_user_list(self):
        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.GET_ALL_SYSTEM_USER
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        
        try:
            auth = Authentications.objects.get(user=self.request.user)
            access_token = auth.access_token
            logger.info("Getting system user list by {} user id".format(auth.user))
        except Exception as e:
            raise InvalidAccessToken("{}".format(e))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer {}'.format(access_token),
        }

        logger.info("Getting system user list from backend with {} url".format(url))
        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
        done = time.time()
        logger.info("Response Status {}".format(response))
        json_data = response.json()
        logger.info("Response time for get system user list is {} sec.".format(done - start_date))
        data = json_data.get('data')
        if response.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info("Received {} system users".format(len(json_data['data'])))
                return data

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))


def _refine_data(system_user_list):
    for system_user in system_user_list:
        if (system_user['created_timestamp'] is not None) and (system_user['created_timestamp'] != "null"):
            created_at = system_user['created_timestamp'] / 1000.0
            system_user['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')
            system_user['fullname'] = '{} {}'.format(system_user['firstname'], system_user['lastname'])

    return system_user_list