from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin
from web_admin import ajax_functions
from web_admin.api_logger import API_Logger
import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


def _format_data(data):
    for i in data:
        i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
    return data


class CardFreezeList(GetHeaderMixin, GroupRequiredMixin, TemplateView):
    group_required = "CAN_VIEW_FREEZE_CARD_LIST"
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
        result_data = _format_data(data)

        permissions = {}
        permissions['CAN_DELETE_FRAUD_TICKET'] = self.check_membership(["CAN_DELETE_FRAUD_TICKET"])
        context = {'data': result_data,
                   'permissions': permissions,
                   }

        self.logger.info('========== End get freeze card ==========')
        return render(request, 'freeze-list.html', context)

    def post(self, request, *args, **kwargs):
        if not self.check_membership(["CAN_DELETE_FRAUD_TICKET"]):
           return JsonResponse({"status": 0, "msg": ""})

        self.logger.info('========== Start delete freeze card ==========')
        context = super(CardFreezeList, self).get_context_data(**kwargs)
        freeze_card_id = context['id']
        url = api_settings.DELETE_FREEZE_CARD_PATH.format(ticket_id=freeze_card_id)

        result = ajax_functions._delete_method(request=request,
                                               api_path=url,
                                               func_description="Delete freeze card",
                                               logger=self.logger,
                                               params=None,
                                               timeout=None)

        self.logger.info('========== End delete freeze card ==========')
        return result

    def get_freeze_card_list(self):
        url = api_settings.SEARCH_TICKET
        params = {}
        is_success, status_code, status_message, data = RestFulClient.post(url=url, headers=self._get_headers(),
                                                                           loggers=self.logger, params=params)
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code, is_getting_list=True)
        if is_success:
            if isinstance(data, list):
                return data
            else:
                return []
