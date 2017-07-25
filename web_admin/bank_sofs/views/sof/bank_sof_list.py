from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods

from datetime import datetime
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from braces.views import GroupRequiredMixin

import logging

logger = logging.getLogger(__name__)


class BankSOFView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_SEARCH_BANK_SOF_CREATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "sof/bank_sof.html"
    search_banks_sof = settings.DOMAIN_NAMES + "report/"+api_settings.API_VERSION+"/banks/sofs"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BankSOFView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search history card ==========')

        search = request.GET.get('search')
        if search is None:
            return render(request, self.template_name)

        user_id = request.GET.get('user_id')
        user_type_id = request.GET.get('user_type_id')
        currency = request.GET.get('currency')
        from_created_timestamp = request.GET.get('from_created_timestamp')
        to_created_timestamp = request.GET.get('to_created_timestamp')

        self.logger.info('Search key "user_id is" is [{}]'.format(user_id))
        self.logger.info('Search key "user_type_id" is [{}]'.format(user_type_id))
        self.logger.info('Search key "currency" is [{}]'.format(currency))
        self.logger.info('Search key "from_created_timestamp" is [{}]'.format(from_created_timestamp))
        self.logger.info('Search key "to_created_timestamp" is [{}]'.format(to_created_timestamp))

        body = {}
        if user_id is not '' and user_id is not None:
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not '0' and user_type_id is not None:
            body['user_type_id'] = int(0 if user_type_id is None else user_type_id)
        if currency is not '' and currency is not None:
            body['currency'] = currency

        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp

        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp

        responses, success = self._get_bank_sof_list(body=body)
        body['from_created_timestamp'] = from_created_timestamp
        body['to_created_timestamp'] = to_created_timestamp

        context = {
            'bank_sof_list': responses,
            'search_by': body
        }

        self.logger.info('========== End search history card ==========')
        return render(request, self.template_name, context)

    def _get_bank_sof_list(self, body):
        return self._post_method(self.search_banks_sof, 'Cash Source of Fund List', logger, body)

