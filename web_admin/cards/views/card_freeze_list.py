from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient

from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin
from web_admin import ajax_functions
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CardFreezeList(GetHeaderMixin, GroupRequiredMixin, TemplateView):
    group_required = "CAN_MANAGE_FREEZE_CARD"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "freeze-list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardFreezeList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start get freeze card ==========')

        data = self.get_freeze_card_list()
        result_data = self.format_data(data)
        context = {'data': result_data}

        self.logger.info('========== End get freeze card ==========')
        return render(request, 'freeze-list.html', context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start delete freeze card ==========')
        context = super(CardFreezeList, self).get_context_data(**kwargs)
        freeze_card_id = context['id']
        url = api_settings.DELETE_FREEZE_CARD_PATH.format(card_id=freeze_card_id)
        result = ajax_functions._delete_method(request, url, "Delete freeze card", self.logger, params=None, timeout=None)
        messages.add_message(
            request,
            messages.SUCCESS,
            'Unfreeze card successfully'
        )
        self.logger.info('========== End delete freeze card ==========')
        return result

    def get_freeze_card_list(self):
        url = api_settings.SEARCH_FREEZE_CARD_PATH
        params = {}
        is_success, status_code, status_message, data = RestFulClient.post(url=url, headers=self._get_headers(), loggers=self.logger, params=params)
        if isinstance(data, list):
            return data
        else:
            return []

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
