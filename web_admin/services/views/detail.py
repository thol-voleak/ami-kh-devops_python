from django.views.generic.base import TemplateView
from django.conf import settings

from authentications.utils import get_auth_header

import requests, time
import logging

logger = logging.getLogger(__name__)


class ServiceDetailForm(TemplateView):
    template_name = "services/detail.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting service detail ==========')

            context = super(ServiceDetailForm, self).get_context_data(**kwargs)
            service_id = context['ServiceId']

            return self._get_service_detail(service_id)

        except:
            context = {'service_info': {}}
            return context

    def _get_service_detail(self, service_id):

        url = settings.SERVICE_DETAIL_URL.format(service_id)

        headers = get_auth_header(self.request.user)

        logger.info("Username: {}".format(self.request.user))
        logger.info('Getting service detail from backend')
        logger.info("URL: {}".format(url))
        start_date = time.time()

        response = requests.get(url, headers=headers, verify=False)

        logger.info("Response Content: {}".format(response.content))
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Received data with response status is {}".format(response.status_code))

        response_json = response.json()
        if response_json['status']['code'] == "success":
            data = response_json.get('data')
            context = {'service_info': data,
                       'add_service_msg': self.request.session.pop('add_service_msg', None)}
            logger.info('========== Finished getting service detail ==========')
            return context
        else:
            logger.info("Error Getting System User Detail.")
            context = {'service_info': response_json.get('data')}
            logger.info('========== Finished getting service detail ==========')
            return context
