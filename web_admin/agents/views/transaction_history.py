from datetime import datetime
from braces.views import GroupRequiredMixin
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import RestFulClient
from web_admin import api_settings
from web_admin import settings
from web_admin import setup_logger
from django.shortcuts import render
from django.views.generic.base import TemplateView

from web_admin.api_logger import API_Logger
from web_admin.api_settings import SOF_TYPES_URL
from web_admin.restful_methods import RESTfulMethods

import logging


logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class TransactionHistoryView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_AGENT_INDIVIDUAL_WALLET"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/transaction_history.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(TransactionHistoryView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting agent transaction history ==========')
        context = super(TransactionHistoryView, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        data = self._get_choices_types()

        # Set first load default time for Context
        from_created_timestamp = datetime.now()
        to_created_timestamp = datetime.now()
        from_created_timestamp = from_created_timestamp.replace(hour=0, minute=0, second=1)
        to_created_timestamp = to_created_timestamp.replace(hour=23, minute=59, second=59)
        new_from_created_timestamp = from_created_timestamp.strftime("%Y-%m-%d")
        new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%d")

        permissions = {
        }

        context = {
            "choices": data,
            'permissions': permissions,
            'agent_id': agent_id,
            'from_created_timestamp': new_from_created_timestamp,
            'to_created_timestamp': new_to_created_timestamp
        }
        self.logger.info('========== Finished getting agent transaction history ==========')
        return render(request, self.template_name, context)

    # def _get_choices_types(self):
    #     data, success = self._get_method(api_path=api_settings.SOF_TYPES_URL,
    #                                      func_description="Choices Type",
    #                                      logger=logger)
    #     return {'sof_types': data}

    def _get_choices_types(self):
        url = settings.DOMAIN_NAMES + SOF_TYPES_URL
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return {'sof_types': data}