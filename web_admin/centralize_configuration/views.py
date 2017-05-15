from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

from django.shortcuts import render
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging
import requests

logger = logging.getLogger(__name__)


class ScopeListView(TemplateView):
    template_name = 'centralize_configuration/scope_list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start get all configuration scope ==========')
        headers = get_auth_header(self.request.user)
        url = settings.DOMAIN_NAMES + settings.SCOPES_URL
        response = requests.get(url=url, headers=headers, verify=settings.CERT)
        logger.info('========== Finished getting api List ==========')
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


class ConfigurationListView(TemplateView):
    template_name = 'centralize_configuration/configuration_list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start get all configuration scope ==========')
        headers = get_auth_header(self.request.user)
        context = super(ConfigurationListView, self).get_context_data(**kwargs)
        scope = context['scope']

        url = settings.DOMAIN_NAMES + settings.GET_CENTRALIZE_CONFIGURATION_URL.format(scope=scope)
        logger.info("Request get configuration scope for {} is {}".format(scope, url))
        response = requests.get(url=url, headers=headers, verify=settings.CERT)
        logger.info('========== Finished getting api List ==========')
        json_data = response.json()
        data = {'scopes': json_data.get('data')}
        logger.info(data)

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
