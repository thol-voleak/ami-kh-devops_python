from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods

from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.global_constants import UserType
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.api_logger import API_Logger

import logging

logger = logging.getLogger(__name__)


class CustomerSOFListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_BANK_SOF_CUSTOMER_PROFILE"
    login_url = 'web:permission_denied'
    raise_exception = False
    searchcustomerbanksofurl = settings.DOMAIN_NAMES + "report/" + api_settings.API_VERSION + "/banks/sofs"

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'member_customer_sof_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CustomerSOFListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting customer sof bank ==========')

        user_id = int(kwargs.get('customerId'))

        self.logger.info('API-Path: {};'.format(self.searchcustomerbanksofurl))
        param = {
            "user_id": user_id,
            "user_type_id": UserType.CUSTOMER.value
        }
        data, success = self._post_method(api_path=self.searchcustomerbanksofurl,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params=param)
        context = {}
        if success:
            cards_list = data.get("bank_sofs", [])
            page = data.get("page", {})
            self.logger.info("Page: {}".format(page))
            context.update(
                {'search_count': page.get('total_elements', 0),
                 'paginator': page,
                 'page_range': calculate_page_range_from_page_info(page),
                 'bank_sof_list': cards_list,
                 'user_id' : user_id,
                 }
            )
        else:
            context.update(
                {'search_count': 0,
                 'paginator': {},
                 'user_id': user_id,
                 'bank_sof_list': [],
                 }
            )

        self.logger.info('========== Finished searching customer sof ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start pagination customer bank SOF ==========')

        user_id = request.POST.get('user_id')
        opening_page_index = request.POST.get('current_page_index')

        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        if user_id is not '' and user_id is not None:
            body['user_id'] = user_id

        context = {}
        data, success, status_message = self._get_bank_sof_list(body=body)
        body['user_type_id'] = UserType.CUSTOMER.value
        if success:
            cards_list = data.get("bank_sofs", [])
            page = data.get("page", {})
            self.logger.info("Page: {}".format(page))
            context.update(
                {'search_count': page.get('total_elements', 0),
                 'paginator': page,
                 'page_range': calculate_page_range_from_page_info(page),
                 'user_id': user_id,
                 'bank_sof_list': cards_list,
                 'search_by': body
                 }
            )
        else:
            context.update(
                {'search_count': 0,
                 'paginator': {},
                 'user_id': user_id,
                 'bank_sof_list': [],
                 'search_by': body
                 }
            )

        self.logger.info('========== End pagination customer bank SOF ==========')
        return render(request, self.template_name, context)

    def _get_bank_sof_list(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=self.searchcustomerbanksofurl,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body)
        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('bank_sofs', []),
                                status_code=status_code, is_getting_list=True)
        return data, success, status_message