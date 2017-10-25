from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.utils import calculate_page_range_from_page_info
from django.shortcuts import render
from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.api_logger import API_Logger
import logging
from django.contrib import messages
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
        context = {"search_count": 0}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search card ==========')

        card_identifier = request.POST.get('card_identifier')
        card_token = request.POST.get('card_token')
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')
        opening_page_index = request.POST.get('current_page_index')

        self.logger.info('card_identifier: {}'.format(card_identifier))
        self.logger.info('card_token: {}'.format(card_token))
        self.logger.info('user_id: {}'.format(user_id))
        self.logger.info('user_type: {}'.format(user_type))

        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        if card_identifier is not '' and card_identifier is not None:
            body['card_identifier'] = card_identifier
        if card_token is not '' and card_token is not None:
            body['token'] = card_token
        if user_id is not '' and user_id is not None:
            body['user_id'] = int(0 if user_id is None else user_id)
        if user_type is not '' and user_type is not '0':
            body['user_type_id'] = int(0 if user_type is None else user_type)

        context = {}
        data, success, status_message = self.get_card_list(body)
        if success:
            cards_list = data.get("cards", [])
            if cards_list is not None:
                cards_list = self.format_data(cards_list)

            page = data.get("page", {})
            context.update(
                {'search_count': page.get('total_elements', 0),
                 'data': cards_list,
                 'paginator': page,
                 'page_range': calculate_page_range_from_page_info(page),
                 'card_identifier': card_identifier,
                 'card_token': card_token,
                 'user_id': user_id,
                 'user_type': user_type,}
            )
        else:
            context.update(
                {'search_count': 0,
                 'data': [],
                 'paginator': {},
                 'card_identifier': card_identifier,
                 'card_token': card_token,
                 'user_id': user_id,
                 'user_type': user_type, }
            )
        self.logger.info('========== End search card ==========')
        return render(request, self.template_name, context)

    def get_card_list(self, body):
        api_path = api_settings.CARD_LIST_PATH

        # api_path = 'http://localhost:4693/search_card_profile'

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body,
                                                                           timeout=settings.GLOBAL_TIMEOUT)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params={}, response=data.get('cards', []),
                                status_code=status_code, is_getting_list=True)

        return data, success, status_message

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_STOP.get(i.get('is_stopped'))
        return data
