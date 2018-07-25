from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.utils import calculate_page_range_from_page_info
from web_admin import setup_logger, api_settings
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin
from web_admin import ajax_functions
from web_admin.restful_helper import RestfulHelper
from datetime import datetime, date, timedelta
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
        context = super(CardFreezeList, self).get_context_data(**kwargs)

        self.logger.info('========== Start get freeze card ==========')
        ticket_id = request.GET.get('ticket_id', None)
        card_id = request.GET.get('card_id', None)
        from_created_date = request.GET.get('from_created_date')
        to_created_date = request.GET.get('to_created_date')
        from_activated_date = request.GET.get('from_activated_date')
        to_activated_date = request.GET.get('to_activated_date')
        is_deleted = request.GET.get('is_deleted')
        if is_deleted == None:
            is_deleted = 'ALL'

        body = {
            # "action": "unstop card",
            "paging": True,
            "page_index": 1

        }

        if ticket_id:
            body['ticket_id'] = ticket_id

        if card_id:
            body['card_id'] = int(card_id)

        if from_created_date is not '' and from_created_date is not None:
            new_from_created_date = datetime.strptime(from_created_date, "%Y-%m-%d")
            new_from_created_date = new_from_created_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_date'] = new_from_created_date

        if to_created_date is not '' and to_created_date is not None:
            new_to_created_date = datetime.strptime(to_created_date, "%Y-%m-%d")
            new_to_created_date = new_to_created_date.replace(hour=23, minute=59, second=59)
            new_to_created_date = new_to_created_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_date'] = new_to_created_date

        if from_activated_date is not '' and from_activated_date is not None:
            new_from_activated_date = datetime.strptime(from_activated_date, "%Y-%m-%d")
            new_from_activated_date = new_from_activated_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_activated_date'] = new_from_activated_date

        if to_activated_date is not '' and to_created_date is not None:
            new_to_activated_date = datetime.strptime(to_activated_date, "%Y-%m-%d")
            new_to_activated_date = new_to_activated_date.replace(hour=23, minute=59, second=59)
            new_to_activated_date = new_to_activated_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_activated_date'] = new_to_activated_date

        if not is_deleted:
            body['is_deleted'] = 1
        else:
            context['is_deleted'] = is_deleted
        if is_deleted in ['0', '1']:
            body['is_deleted'] = int(is_deleted)

        opening_page_index = request.GET.get('current_page_index')
        if opening_page_index:
            body['page_index'] = int(opening_page_index)
            context['current_page_index'] = int(opening_page_index)
        is_success, data = self.get_freeze_card_list(body)
        if is_success :
            result_data = data.get('tickets')
            self.logger.info(result_data)
            # result_data = _format_data(data.get('tickets'))
            page = data.get("page",{})
            permissions = {}
            permissions['CAN_DELETE_FRAUD_TICKET'] = self.check_membership(["CAN_DELETE_FRAUD_TICKET"])
            context.update ({'data': result_data,
                             'permissions': permissions,
                             'paginator': page,
                             'page_range': calculate_page_range_from_page_info(page),
                             'ticket_id': str("" if ticket_id is None else ticket_id),
                             'card_id': str("" if card_id is None else card_id)
                             })

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

    def get_freeze_card_list(self, body):
        url = api_settings.SEARCH_TICKET

        # is_success, status_code, status_message, data = RestFulClient.post(url=url, headers=self._get_headers(),
        #                                                                    loggers=self.logger, params=body)
        # API_Logger.post_logging(loggers=self.logger, params=body, response=data,
        #                         status_code=status_code, is_getting_list=True)
        success, status_code, status_message, data = RestfulHelper.send("POST", url, body, self.request,
                                                                        "searching ticket",
                                                                        log_count_field='data.tickets')
        # if success:
        #     if isinstance(data.get('tickets'), list):
        #         return success, data
        #     else:
        #         return []
        if success:
            return success, data
        else:
            return success, status_message
