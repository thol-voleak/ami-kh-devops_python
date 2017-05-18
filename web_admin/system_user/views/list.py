import datetime
import logging
import time

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "system_user/system_user_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get system user List ==========')
        data = self.get_system_user_list()
        logger.info('========== Finished get system user List ==========')
        result = {'data': data,
                'created_msg': self.request.session.pop('system_user_create_msg', None),
                'del_msg': self.request.session.pop('system_user_delete_msg', None),
                'pw_msg': self.request.session.pop('system_user_change_password_msg', None)}
        return result

    def get_system_user_list(self):
        url = settings.GET_ALL_SYSTEM_USER

        logger.info("Getting system user list from backend with {} url".format(url))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
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
