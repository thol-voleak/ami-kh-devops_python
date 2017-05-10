from django.views.generic.base import TemplateView
from django.conf import settings

from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken
import requests, time
import logging

logger = logging.getLogger(__name__)

class ServiceGroupDetailForm(TemplateView):
    template_name = "service_group/detail.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting service group detail ==========')

            context = super(ServiceGroupDetailForm, self).get_context_data(**kwargs)
            service_group_id = context['ServiceGroupId']

            return self._get_service_group_detail(service_group_id)

        except:
            context = {'service_group_info': {}}
            return context


    def _get_service_group_detail(self, service_group_id):

        url = settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)

        headers = get_auth_header(self.request.user)

        logger.info("Username: {}".format(self.request.user))
        logger.info('Getting service group detail from backend')
        logger.info("URL: {}".format(url))
        start_date = time.time()

        response = requests.get(url, headers=headers, verify=settings.CERT)

        logger.info("Response Content: {}".format(response.content))
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Received data with response status is {}".format(response.status_code))

        response_json = response.json()
        status = response_json.get('status', {})
        # if not isinstance(status, dict):
        #     status = {}
        code = status.get('code', '')

        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data')
            context = {'service_group_info': data,
                       'add_service_group_msg': self.request.session.pop('add_service_group_msg', None),
                       'service_group_update_msg': self.request.session.pop('service_group_update_msg', None)}
            logger.info('========== Finished getting service group detail ==========')
            return context
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

            logger.info("Error Getting System User Detail.")
            context = {'service_group_info': response_json.get('data')}
            logger.info('========== Finished getting service group detail ==========')
            return context


