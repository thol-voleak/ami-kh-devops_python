from braces.views import GroupRequiredMixin
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
import logging

logger = logging.getLogger(__name__)


class ConfigurationListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = 'centralize_configuration/configuration_list.html'
    logger = logger

    group_required = "SYS_CONFIGURE_SCOPE"
    login_url = 'web:web-index'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ConfigurationListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting all configuration scope ==========')
        context = super(ConfigurationListView, self).get_context_data(**kwargs)
        scope = context['scope']
        url = api_settings.CONFIGURATION_URL.format(scope=scope)
        data, success = self._get_method(url, 'configuration scope', logger)
        if success:
            is_permission_scope_attr = check_permissions_by_user(self.request.user, "SYS_EDIT_SCOPE_ATTRIBUTE")
            context["configurations"] = data
            context["scope_name"] = scope
            context["is_permission_scope_attr"] = is_permission_scope_attr
            self.logger.info('========== Finish getting all configuration scope ==========')
            return context


class ConfigurationDetailsView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = 'centralize_configuration/configuration_details.html'
    logger = logger

    group_required = "SYS_EDIT_SCOPE_ATTRIBUTE"
    login_url = 'web:web-index'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ConfigurationDetailsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting configuration scope details ==========')
        context = super(ConfigurationDetailsView, self).get_context_data(**kwargs)
        scope = context['scope']
        conf_key = context['conf_key']
        url = api_settings.CONFIGURATION_DETAIL_URL.format(scope=scope, key=conf_key)

        data, success = self._get_method(url, 'configuration scope details', logger)
        if success:
            self.logger.info(
                '========== Finish getting configuration scope details ==========')
            context["configurations"] = data
            context["scope_name"] = scope
            context["user"] = self.request.user
            return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating configuration scope ==========')
        scope = kwargs.get('scope', None)
        conf_key = kwargs.get('conf_key', None)
        conf_value = request.POST.get('conf_value')

        url = settings.DOMAIN_NAMES + api_settings.CONFIGURATION_UPDATE_URL.format(
            scope=scope, key=conf_key)
        params = {'value': conf_value}

        data, success = self._put_method(url, 'configuration scope', logger, params)
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
                data
            )
        self.logger.info('========== Finish updating configuration scope ==========')
        return redirect('centralize_configuration:configuration_list', scope=scope)
