from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods

import logging

logger = logging.getLogger(__name__)


class ConfigurationListView(TemplateView, RESTfulMethods):
    template_name = 'centralize_configuration/configuration_list.html'

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting all configuration scope ==========')
            context = super(ConfigurationListView, self).get_context_data(**kwargs)
            scope = context['scope']
            url = api_settings.CONFIGURATION_URL.format(scope=scope)
            data, success = self._get_method(url, 'configuration scope', logger)
            if success:
                logger.info('========== Finish getting all configuration scope ==========')
                context["configurations"] = data
                context["scope_name"] = scope
                return context
        except Exception as e:
            raise Exception(e)


class ConfigurationDetailsView(TemplateView, RESTfulMethods):
    template_name = 'centralize_configuration/configuration_details.html'

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting configuration scope details ==========')
            context = super(ConfigurationDetailsView, self).get_context_data(**kwargs)
            scope = context['scope']
            conf_key = context['conf_key']
            url = api_settings.CONFIGURATION_DETAIL_URL.format(scope=scope, key=conf_key)

            data, success = self._get_method(url, 'configuration scope details', logger)
            if success:
                logger.info(
                    '========== Finish getting configuration scope details ==========')
                context["configurations"] = data
                context["scope_name"] = scope
                return context
        except Exception as e:
            return Exception(e)

    def post(self, request, *args, **kwargs):
        try:
            logger.info('========== Start updating configuration scope ==========')
            scope = kwargs.get('scope', None)
            conf_key = kwargs.get('conf_key', None)
            conf_value = request.POST.get('conf_value')

            url = settings.DOMAIN_NAMES + api_settings.CONFIGURATION_DETAIL_URL.format(
                scope=scope, key=conf_key)
            params = {
                'value': conf_value
            }

            data, success = self._post_method(url, 'configuration scope', logger, params)
            if success:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Please restart service to get configuration effect.'
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Something wrong happened.'
                )
            logger.info('========== Finish updating configuration scope ==========')
            return redirect('centralize_configuration:configuration_list', scope=scope)
        except Exception as e:
            raise Exception(e)
