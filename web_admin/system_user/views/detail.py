
import logging
import time

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class DetailView(TemplateView):
    template_name = "system_user/system_user_detail.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting system user detail ==========')
            context = super(DetailView, self).get_context_data(**kwargs)
            system_user_id = context['systemUserId']

            return self._get_system_user_detail(system_user_id)

        except:
            context = {'system_user_info': {}}
            return context

    def _get_system_user_detail(self, system_user_id):

        url = settings.SYSTEM_USER_DETAIL_URL.format(system_user_id)

        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        logger.info("URL: {}".format(url))
        done = time.time()
        response_json = response.json()
        logger.info("Response content for get system user detail: {}".format(response_json))
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Response status: {}".format(response.status_code))

        if response_json['status']['code'] == "success":
            logger.info("Client detail was fetched.")
            data = response_json.get('data')
            context = {'system_user_info': data,
                      'msg': self.request.session.pop('system_user_update_msg', None)
            }
            logger.info('========== Finished getting system user detail ==========')
            return context

        if response_json["status"]["message"] == "Invalid access token":
            raise InvalidAccessToken(response_json["status"]["message"])
