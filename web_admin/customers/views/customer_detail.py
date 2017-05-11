import logging
import time
import requests

from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class CustomerDetailView(TemplateView, GetHeaderMixin):
    template_name = 'customer_detail.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting customer detail ==========')

        customer_id = int(kwargs.get('customerId'))
        data = self.get_member_detail(customer_id=customer_id)        
        logger.info('========== Finished getting customer detail ==========')

        return data
        
    def get_member_detail(self, customer_id):
        api_path = settings.MEMBER_CUSTOMER_PATH
        url = settings.DOMAIN_NAMES + api_path

        logger.info('API-Path: {}/{};'.format(api_path, customer_id))
        #logger.info('Param : {}'.format(customer_id))
        
        body = {}

        start = time.time()
        response = requests.post(url, headers=self._get_headers(), json=body, verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {};".format(response.status_code))
        logger.info("Response_time: {} sec.".format(end - start))

        response_json = response.json()

        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')

        

        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data', [])
            for i in data:
                if i['id'] == customer_id:

                    logger.info("Response_content: {}".format(i))
                    context = {'customer_info': i,
                               'msg': self.request.session.pop('msg', None)}
                    return context
            return {}
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)
            return {}
