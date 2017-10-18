from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView
from django.shortcuts import render
from datetime import datetime , timedelta
from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken


import logging

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_SEARCH_CUSTOMER"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'member_customer_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        params = {}
        customers = {}
        is_success = False
        status_code = ''
        url = api_settings.MEMBER_CUSTOMER_PATH
        context = super(ListView, self).get_context_data(**kwargs)
        #set default date
        to_created_timestamp = datetime.now()
        to_created_timestamp = to_created_timestamp.replace(hour=23, minute=59, second=59)
        current_day = to_created_timestamp.day
        first_day = to_created_timestamp.replace(day=1)
        prev_month_lastday = first_day - timedelta(days=1)
        last_day = prev_month_lastday.day
        if current_day > last_day:
            current_day = last_day
        
        new_from_created_timestamp = prev_month_lastday.replace(day=current_day)
        new_from_created_timestamp = new_from_created_timestamp.strftime("%Y-%m-%d")
        context['from_created_timestamp'] = new_from_created_timestamp
        
        new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%d")
        context['to_created_timestamp'] = new_to_created_timestamp



        self.logger.info('========== Start searching Customer ==========')
        opening_page_index = request.GET.get('current_page_index')
        customer_id = request.GET.get('customer_id')
        unique_reference = request.GET.get('unique_reference')
        kyc_status = request.GET.get('kyc_status')
        citizen_card_id = request.GET.get('citizen_card_id')
        email = request.GET.get('email')
        mobile_number = request.GET.get('mobile_number')
        from_created_timestamp = request.GET.get('from_created_timestamp')
        to_created_timestamp = request.GET.get('to_created_timestamp')
        if customer_id is None and unique_reference is None \
           and kyc_status is None and citizen_card_id is None \
           and email is None and mobile_number is None:
           customers = {}
        else:
            params['paging'] = True
            params['page_index'] = int(opening_page_index)
            if customer_id:
                params['id'] = customer_id
                context['customer_id'] = customer_id
            if unique_reference:
                params['unique_reference'] = unique_reference
                context['unique_reference'] = unique_reference
            if kyc_status:
                kyc_status_code = int(kyc_status)
                params['kyc_status'] = kyc_status_code
                context['kyc_status'] = kyc_status
            if citizen_card_id:
                params['citizen_card_id'] = citizen_card_id
                context['citizen_card_id'] = citizen_card_id
            if email:
                params['email'] = email
                context['email'] = email
            if mobile_number:
                params['mobile_number'] = mobile_number
                context['mobile_number'] = mobile_number
            if from_created_timestamp:
                new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
                new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
                params['from_created_timestamp'] = new_from_created_timestamp
                context['from_created_timestamp'] = from_created_timestamp
            if to_created_timestamp:
                new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
                new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
                new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
                params['to_created_timestamp'] = new_to_created_timestamp
                context['to_created_timestamp'] = to_created_timestamp
            is_success, status_code, status_message, data = RestFulClient.post(
                                                    url= url,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=params)
            self.logger.info("Params: {} ".format(params))
        if is_success:
            customers = data['customers']
            page = data['page']
            count = len(customers)
            self.logger.info("Response_content_count:{}".format(count))

            is_permission_detail = check_permissions_by_user(self.request.user, 'CAN_VIEW_DETAIL_MEMBER_CUSTOMER_PROFILE')
            is_permission_update = check_permissions_by_user(self.request.user,'CAN_EDIT_MEMBER_CUSTOMER_PROFILE')
            is_permission_sof_bank = check_permissions_by_user(self.request.user, 'CAN_VIEW_BANK_SOF_CUSTOMER_PROFILE')
            is_permission_identity = check_permissions_by_user(self.request.user, 'CAN_VIEW_IDENTITY_CUSTOMER')
            is_permission_suspend = check_permissions_by_user(self.request.user, 'CAN_SUSPEND_CUSTOMER')
            for i in data['customers']:
                i['is_permission_detail'] = is_permission_detail
                i['is_permission_update'] = is_permission_update
                i['is_permission_sof_bank'] = is_permission_sof_bank
                i['is_permission_identity'] = is_permission_identity
                i['is_permission_suspend'] = is_permission_suspend

            context.update({'paginator': page, 'page_range': calculate_page_range_from_page_info(page)})
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)


        context['data'] = customers
            
        self.logger.info('========== Finished searching Customer ==========')
        return render(request, 'member_customer_list.html', context)

