from authentications.apps import InvalidAccessToken
from authentications.models import *

import logging
import random
import string
import time
import requests

from django.conf import settings
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

logger = logging.getLogger(__name__)


class DeleteView(TemplateView):
    template_name = "system_user/delete_system_user.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting system user detail ==========')
            context = super(DeleteView, self).get_context_data(**kwargs)
            system_user_id = context['system_user_id']

            return self._get_system_user_detail(system_user_id)
        except:
            context = {'system_user_info': {}}
            return context

    def _get_system_user_detail(self, system_user_id):

        url = settings.SYSTEM_USER_DETAIL_URL.format(system_user_id)
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        try:
            auth = Authentications.objects.get(user=self.request.user)
            logger.info("Username: {}".format(self.request.user.username))
            access_token = auth.access_token
        except Exception as e:
            raise InvalidAccessToken("{}".format(e))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer ' + access_token,
        }
        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
        logger.info("URL for deleting system user id {} is {}".format(system_user_id, url))
        done = time.time()
        response_json = response.json()
        logger.info("Response content for get system user detail: {}".format(response_json))
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Response status: {}".format(response.status_code))

        if response_json['status']['code'] == "success":
            logger.info("system user detail was fetched.")
            data = response_json.get('data')
            context = {'system_user_info': data}
            logger.info('========== Finished getting system user detail ==========')
            return context

        if response_json["message"] == "Invalid access token":
            raise InvalidAccessToken(response_json["message"])

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            system_user_id = kwargs['system_user_id']
            logger.info("========== Start deleting system user ==========")
            logger.info('system user ID to be deleted: {}'.format(system_user_id))
            logger.info('Username: {}'.format(request.user.username))

            url = settings.DELETE_SYSTEM_USER_URL.format(system_user_id)
            try:
                auth = Authentications.objects.get(user=request.user)
                access_token = auth.access_token
            except Exception as e:
                raise InvalidAccessToken("{}".format(e))

            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            headers = {
                'content-type': 'application/json',
                'correlation-id': correlation_id,
                'client_id': settings.CLIENTID,
                'client_secret': settings.CLIENTSECRET,
                'Authorization': 'Bearer {}'.format(access_token),
            }

            logger.info('URL: {}'.format(url))
            start_date = time.time()
            response = requests.delete(url, headers=headers, verify=False)
            done = time.time()
            logger.info(
                "Response time for delete {} system user id is {} sec.".format(system_user_id, done - start_date))
            logger.info("Response code for delete {} system user id is {}".format(system_user_id, response.status_code))
            logger.info("Response for delete {} system user id is {}".format(system_user_id, response.content))

            if response.status_code == 200:
                response_json = response.json()
                status = response_json['status']

                if status['code'] == "success":
                    logger.info("system user was deleted.")
                    logger.info("========== Finished deleting system user id ==========")
                    request.session['system_user_delete_msg'] = 'Deleted data successfully'
                    return HttpResponseRedirect(reverse('system_user:system-user-list', args=(None)))
                else:
                    logger.info("Error deleting system user {}".format(system_user_id))
                    logger.info("========== Finished deleting system user id ==========")
            else:
                logger.info("Error deleting system user {}".format(system_user_id))
                logger.info("========== Finished deleting system user id ==========")

        except Exception as e:
            logger.info('Exception:')
            logger.info(e)
            logger.info("========== Finished deleting system user id ==========")