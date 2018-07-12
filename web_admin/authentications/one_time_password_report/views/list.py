from web_admin import setup_logger, RestFulClient, api_settings
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin.utils import calculate_page_range_from_page_info, convert_string_to_date_time
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from braces.views import GroupRequiredMixin
from datetime import date, timedelta

import logging

logger = logging.getLogger(__name__)


class OTPList(GroupRequiredMixin, TemplateView):

    template_name = "one_time_password_report/list.html"
    logger = logger

    group_required = "CAN_MANAGE_OTP_REPORT"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(OTPList, self).dispatch(request, *args, **kwargs)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def get(self, request, *args, **kwargs):
        context = super(OTPList, self).get_context_data(**kwargs)
        self.logger.info('========== Start getting otp list ==========')

        self.initSearchDateTime(context)

        body= {'paging': True, 'page_index': 1}
        otp_list, is_success = self.get_otp_list(body)
        page = otp_list.get("page", {})
        context.update({
            'delivery_channel': 'All',
            'user_type': 'All',
            'is_success_verified': 'All',
            'otp_list': otp_list['otps'],
            'paginator': page,
            'search_count': page.get('total_elements', 0),
            'page_range': calculate_page_range_from_page_info(page),
        })

        self.logger.info('========== Finish getting otp list ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(OTPList, self).get_context_data(**kwargs)
        self.logger.info('========== Start searching otp list ==========')
        user_id = request.POST.get('user_id', '')
        delivery_channel = request.POST.get('delivery_channel', '')
        user_ref_code = request.POST.get('user_ref_code', '')
        otp_id = request.POST.get('otp_id', '')
        email = request.POST.get('email', '')
        is_deleted = request.POST.get('is_deleted', '')
        mobile_number = request.POST.get('mobile_number', '')
        otp_reference_id = request.POST.get('otp_reference_id', '')
        is_success_verified = request.POST.get('is_success_verified', '')
        opening_page_index = request.POST.get('current_page_index')
        user_type = request.POST.get('user_type', '')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        from_time = request.POST.get('from_time')
        to_time = request.POST.get('to_time')

        body = {}
        if user_id:
            body['user_id'] = user_id
        if delivery_channel:
            if delivery_channel != 'All':
                body['delivery_channel'] = delivery_channel
        else:
            body['delivery_channel'] = None
        if user_ref_code:
            body['user_reference_code'] = user_ref_code
        if otp_id:
            body['id'] = otp_id
        if email:
            body['email'] = email
        if mobile_number:
            body['mobile_number'] = mobile_number
        if otp_reference_id:
            body['otp_reference_id'] = otp_reference_id
        if is_deleted:
            body['is_deleted'] = True if is_deleted == '1' else False
        if is_success_verified and is_success_verified != 'All':
            body['is_success_verified'] = True if is_success_verified == 'Yes' else False
        if user_type and user_type != 'All':
            body['user_type'] = user_type

        if from_created_timestamp:
            body['from'] = convert_string_to_date_time(from_created_timestamp, from_time)

        if to_created_timestamp:
            body['to'] = convert_string_to_date_time(to_created_timestamp, to_time)

        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        otp_list, is_success = self.get_otp_list(body)
        page = otp_list.get("page", {})
        context.update({
            'otp_id': otp_id,
            'is_deleted': is_deleted,
            'user_id': user_id,
            'user_ref_code': user_ref_code,
            'delivery_channel': delivery_channel,
            'email': email,
            'mobile_number': mobile_number,
            'otp_reference_id': otp_reference_id,
            'is_success_verified': is_success_verified,
            'user_type': user_type,
            'from_date': from_created_timestamp,
            'to_date': to_created_timestamp,
            'from_time': from_time,
            'to_time': to_time,
            'search_count': page.get('total_elements', 0),
            'otp_list': otp_list['otps'],
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page),
        })
        self.logger.info('========== Finish searching otp list ==========')
        return render(request, self.template_name, context)

    def get_otp_list(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.OTP_URL,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)
        if not is_success:
            data = {'otps': []}

            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
        API_Logger.post_logging(loggers=self.logger, params=body, response=data['otps'],
                                status_code=status_code, is_getting_list=True)

        return data, is_success

    def initSearchDateTime(self, context):
        today = date.today()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)
        context['from_date'] = yesterday.strftime('%Y-%m-%d')
        context['to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['from_time'] = "00:00:00"
        context['to_time'] = "00:00:00"
