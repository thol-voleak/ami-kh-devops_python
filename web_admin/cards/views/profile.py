from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

from django.shortcuts import render
from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger, RestFulClient

import logging

logger = logging.getLogger(__name__)

IS_STOP = {
    True: 'YES',
    False: 'NO',
}


class ProfileView(GroupRequiredMixin, GetHeaderMixin, TemplateView):
    group_required = "CAN_SEARCH_CARD_PROFILE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "profile.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search card ==========')

        card_identifier = request.GET.get('card_identifier')
        card_token = request.GET.get('card_token')
        user_id = request.GET.get('user_id')
        user_type = request.GET.get('user_type')

        self.logger.info('card_identifier: {}'.format(card_identifier))
        self.logger.info('card_token: {}'.format(card_token))
        self.logger.info('user_id: {}'.format(user_id))
        self.logger.info('user_type: {}'.format(user_type))

        body = {}
        
        if card_identifier is not '' and card_identifier is not None:
            body['card_identifier'] = card_identifier
        if card_token is not '' and card_token is not None:
            body['token'] = card_token
        if user_id is not '' and user_id is not None:
            body['user_id'] = int(0 if user_id is None else user_id)
        if user_type is not '' and user_type is not '0':
            body['user_type_id'] = int(0 if user_type is None else user_type)

        data = self.get_card_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        permissions = {}
        permissions['CAN_FREEZE_CARD'] = check_permissions_by_user(self.request.user, 'CAN_FREEZE_CARD')

        context = {'data': result_data,
                   'card_identifier': card_identifier,
                   'card_token': card_token,
                   'user_id': user_id,
                   'user_type': user_type,
                   'search_count': len(data),
                   'permissions': permissions
                   }

        self.logger.info('========== End search card ==========')
        return render(request, 'profile.html', context)

    def get_card_list(self, body):
        api_path = api_settings.CARD_LIST_PATH

        is_success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        if isinstance(data, list):
            self.logger.info('Response_content_count: {}'.format(len(data)))
            return data
        else:
            return []

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_STOP.get(i.get('is_stopped'))
        return data
