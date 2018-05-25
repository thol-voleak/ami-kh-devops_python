from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from braces.views import GroupRequiredMixin
from django.contrib import messages
import pdb

logger = logging.getLogger(__name__)

class FileList(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "files/list.html"
    group_required = "CAN_SEARCH_UPLOAD"
    login_url = 'web:permission_denied'
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(FileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start render bulk-upload file list page==========')
        status_list = self._get_status_list()
        function_list = self._get_function_list()

        pdb.set_trace()
        context = {
            'status_list': status_list,
            'function_list': function_list,
        }
        self.logger.info('========== Finish render bulk-upload file list page==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        function_list = self._get_function_list()

        function = int(request.POST.get('function'))

        body = {}
        if function!=0:
            body['function_id'] = function

        context = {
            'function_list': function_list,
        }
        return render(request, self.template_name, context)


    def _get_status_list(self):
        return [
            {"name": "All", "value": ""},
        ]

    def _get_function_list(self):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.SEARCH_FUNCTION,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params={})

        API_Logger.post_logging(loggers=self.logger, params={}, response=data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        data=[{"id":0,"name":"All"}]+data
        return data


    def _search_file(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.SEARCH_UPLOADED_FILE,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data

    def _post_file(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.POST_UPLOADED_FILE,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data
