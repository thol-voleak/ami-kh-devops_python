from django.conf import settings
from web_admin import api_settings, setup_logger
from django.http import Http404
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username
from services.views.mixins import GetCommandNameAndServiceNameMixin
from web_admin.restful_methods import RESTfulMethods

import logging

logger = logging.getLogger(__name__)


class FeeTierListView(TemplateView, GetCommandNameAndServiceNameMixin, RESTfulMethods):
    template_name = "services/tier/tier_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(FeeTierListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(FeeTierListView, self).get_context_data(*args, **kwargs)
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')
        if not service_id or not service_command_id:
            raise Http404

        self.logger.info('========== Start get Fee Tier List ==========')
        data, success = self._get_fee_tier_list(service_command_id)
        self.logger.info('========== Finished get Fee Tier List ==========')

        context['data'] = data
        context['msg'] = self.request.session.pop('add_tier_msg', None)
        context['edit_msg'] = self.request.session.pop('edit_tier_msg', None)
        context['delete_msg'] = self.request.session.pop('delete_tier_msg', None)

        self.logger.info('========== Start get service name ==========')
        context['service_name'] = self._get_service_name_by_id(service_id)
        self.logger.info('========== Finish get service name ==========')

        self.logger.info('========== Start get command name ==========')
        context['command_name'] = self._get_command_name_by_id(command_id)
        self.logger.info('========== Finish get command name ==========')

        return context

    def _get_fee_tier_list(self, service_command_id):
        url = settings.DOMAIN_NAMES + api_settings.FEE_TIER_LIST.format(service_command_id=service_command_id)
        return self._get_precision_method(url, "fee tier list", logger)
