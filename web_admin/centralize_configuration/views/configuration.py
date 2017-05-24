from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from web_admin import api_settings

import logging
import requests

logger = logging.getLogger(__name__)


class ConfigurationListView(TemplateView):
    template_name = 'centralize_configuration/configuration_list.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start get all configuration scope ==========')
        headers = get_auth_header(self.request.user)
        context = super(ConfigurationListView, self).get_context_data(**kwargs)
        scope = context['scope']
        url = settings.DOMAIN_NAMES + api_settings.CONFIGURATION_URL.format(
            scope=scope)

        logger.info("Request get configuration scope for {} is {}".format(scope, url))
        response = requests.get(url=url, headers=headers, verify=settings.CERT)

        json_data = response.json()
        status = json_data.get('status', '')
        data = json_data.get('data')
        logger.info(json_data)

        if response.status_code == 200 and status.get('code', '') == "success":
            logger.info("All scope is {} scopes".format(len(json_data.get('data'))))
            logger.info('========== End get all configuration scope ==========')
            context["configurations"] = data
            context["scope_name"] = scope
            return context
        else:
            if status.get('code', '') == "access_token_expire":
                logger.info('========== End get all configuration scope ==========')
                raise InvalidAccessToken(status.get('message', ''))

        raise Exception(response.content)


class ConfigurationDetailsView(TemplateView):
    template_name = 'centralize_configuration/configuration_details.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start get configuration scope details ==========')
        headers = get_auth_header(self.request.user)
        context = super(ConfigurationDetailsView, self).get_context_data(**kwargs)
        scope = context['scope']
        conf_key = context['conf_key']
        url = settings.DOMAIN_NAMES + api_settings.CONFIGURATION_DETAIL_URL.format(
            scope=scope, key=conf_key)

        response = requests.get(url=url, headers=headers, verify=settings.CERT)
        json_data = response.json()
        status = json_data.get('status', '')
        data = json_data.get('data')
        logger.info(json_data)

        if response.status_code == 200 and status.get('code', '') == "success":
            logger.info("All scope is {} scopes".format(len(json_data.get('data'))))
            logger.info('========== End get all configuration scope ==========')
            context["configurations"] = data
            context["scope_name"] = scope
            conf_key = context['conf_key']
            return context
        else:
            if status.get('code', '') == "access_token_expire":
                logger.info('========== End get configuration scope details ==========')
                raise InvalidAccessToken(status.get('message', ''))

        raise Exception(response.content)

    def post(self, request, *args, **kwargs):
        logger.info('========== Start update configuration scope ==========')
        scope = kwargs.get('scope', None)
        conf_key = kwargs.get('conf_key', None)
        conf_value = request.POST.get('conf_value')

        headers = get_auth_header(self.request.user)
        url = settings.DOMAIN_NAMES + api_settings.CONFIGURATION_DETAIL_URL.format(
            scope=scope, key=conf_key)
        params = {
            'value': conf_value
        }

        response = requests.put(url=url, headers=headers, json=params, verify=settings.CERT)
        json_data = response.json()
        status = json_data.get('status', '')
        data = json_data.get('data')
        logger.info(json_data)

        messages.add_message(
            request,
            messages.ERROR,
            'Please restart service to get configuration effect.'
        )

        if response.status_code == 200 and status.get('code', '') == "success":
            return redirect('centralize_configuration:configuration_list', scope=scope)
        else:
            if status.get('code', '') == "access_token_expire":
                logger.info('========== End update configuration scope ==========')
                raise InvalidAccessToken(status.get('message', ''))

        raise Exception(response.content)
