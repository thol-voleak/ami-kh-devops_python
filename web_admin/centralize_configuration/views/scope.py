from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin import api_settings

import logging
import requests

logger = logging.getLogger(__name__)


class ScopeListView(TemplateView):
    template_name = 'centralize_configuration/scope_list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start get all configuration scope ==========')
        url = settings.DOMAIN_NAMES + api_settings.SCOPES_URL
        headers = get_auth_header(self.request.user)

        response = requests.get(url=url, headers=headers, verify=settings.CERT)
        json_data = response.json()
        data = {'scopes': json_data.get('data')}

        status = json_data.get('status', {})
        if status.get('code', '') == "success":
            logger.info("All scope is {} scopes".format(len(data)))
            logger.info('========== End get all configuration scope ==========')
            return data
        else:
            if status.get('code', '') == "access_token_expire":
                logger.info('========== End get all configuration scope ==========')
                raise InvalidAccessToken(status.get('message', ''))
        raise Exception(response.content)
