from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

from datetime import datetime
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from braces.views import GroupRequiredMixin

from authentications.apps import InvalidAccessToken
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin

import logging

logger = logging.getLogger(__name__)


class CardSOFView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_SEARCH_CARD_SOF_CREATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "sof/card_sof.html"
    search_card_sof_path = settings.DOMAIN_NAMES + "report/"+api_settings.API_VERSION+"/cards/sofs"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardSOFView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search history card SOF ==========')

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

        responses, success = self._get_card_sof_list(body=body)
        self.logger.info('Response_content_count: {}'.format(len(responses)))
        body['from_created_timestamp'] = from_created_timestamp
        body['to_created_timestamp'] = to_created_timestamp

        context = {
            'card_sof_list': responses,
            'search_by': body
        }

        self.logger.info('========== End search history card ==========')
        return render(request, self.template_name, context)

    def _get_card_sof_list(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=self.search_card_sof_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)
        return data, is_success
