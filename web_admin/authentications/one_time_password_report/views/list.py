from web_admin import setup_logger, RestFulClient, api_settings
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin.utils import calculate_page_range_from_page_info
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger

import logging

logger = logging.getLogger(__name__)


class OTPList(TemplateView):

    template_name = "one_time_password_report/list.html"
    logger = logger

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

        body= {}
        body['paging'] = True
        body['page_index'] = 1
        otp_list, is_success = self.get_otp_list(body)
        page = otp_list.get("page", {})
        converted_otp_list = self.__handle_validator(otp_list['otps'])
        context.update({
            'otp_list': converted_otp_list,
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
        opening_page_index = request.POST.get('current_page_index')
        body = {}
        if user_id:
            body['user_id'] = user_id
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        otp_list, is_success = self.get_otp_list(body)
        page = otp_list.get("page", {})
        converted_otp_list = self.__handle_validator(otp_list['otps'])
        context.update({
            'user_id': user_id,
            'search_count': page.get('total_elements', 0),
            'otp_list': converted_otp_list,
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

        API_Logger.post_logging(loggers=self.logger, params=body, response=data['otps'],
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
        return data, is_success

    def __handle_validator(self, otp_list):

        for otp in otp_list:
            otp['is_passed_validation'] = False
            otp['failed_validation_count'] = len(otp['verifications'])
            for validator in otp['verifications']:
                if validator['is_success']:
                    otp['is_passed_validation'] = True
                    otp['failed_validation_count'] = len(otp['verifications']) - 1
                    break
        return otp_list
