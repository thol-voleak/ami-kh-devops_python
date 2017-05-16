import logging
import time

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header
from django.contrib import messages

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

    def post(self, request, *args, **kwargs):
        try:
            system_user_id = kwargs['system_user_id']
            logger.info("========== Start deleting system user ==========")
            logger.info('system user ID to be deleted: {}'.format(system_user_id))
            logger.info('Username: {}'.format(request.user.username))

            url = settings.DELETE_SYSTEM_USER_URL.format(system_user_id)

            logger.info('URL: {}'.format(url))
            start_date = time.time()
            response = requests.delete(url, headers=get_auth_header(request.user),
                                       verify=settings.CERT)
            done = time.time()
            logger.info(
                "Response time for delete {} system user id is {} sec.".format(system_user_id, done - start_date))
            logger.info("Response code for delete {} system user id is {}".format(system_user_id, response.status_code))
            logger.info("Response for delete {} system user id is {}".format(system_user_id, response.content))
            response_json = response.json()
            status = response_json.get('status', {})
            code = status.get('code', '')
            if (code == "access_token_expire") or (code== 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
            

            if response.status_code == 200:
                response_json = response.json()
                status = response_json['status']

                if status['code'] == "success":
                    logger.info("system user was deleted.")
                    logger.info("========== Finished deleting system user id ==========")
                    messages.add_message(request, messages.SUCCESS, 'Deleted data successfully')
                    return redirect('system_user:search')
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

    def _get_system_user_detail(self, system_user_id):

        url = settings.SYSTEM_USER_DETAIL_URL.format(system_user_id)
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
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

        if response_json["status"]["message"] == "Invalid access token":
            raise InvalidAccessToken(response_json["status"]["message"])
