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
from web_admin.utils import calculate_page_range_from_page_info

logger = logging.getLogger(__name__)

status_list_map = {
    "All": 0,
    "VALIDATING": 1,
    "VALIDATE_FAIL": 2,
    "VALIDATED": 3,
    "POSTING": 4,
    "POST_FAIL": 5,
    "POST_PARTIAL": 6,
    "POSTED": 7
}

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
        function_list = self._get_function_list()

        context = {
            'function_id':0,
            'status_id':0,
            'status_list_map': status_list_map,
            'function_list': function_list,
            'search_count': 0
        }
        self.logger.info('========== Finish render bulk-upload file list page==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        opening_page_index = request.POST.get('current_page_index')


        function = int(request.POST.get('function'))
        function_list = self._get_function_list()
        status = int(request.POST.get('status'))

        filename = request.POST.get('filename')
        file_id = request.POST.get('file_id')
        uploaded_by = request.POST.get('uploaded_by')
        uploaded_from = request.POST.get('uploaded_from')
        uploaded_to = request.POST.get('uploaded_to')

        postingFileId = request.POST.get('postingFileId')

        body = {}
        body['page_index'] = int(opening_page_index)
        if filename!='':
            body['file_name'] = filename
        if file_id:
            body['id'] = int(file_id)
        if uploaded_by:
            body['uploaded_username'] = uploaded_by
            # if uploaded_from:
        if function!=0:
            body['function_id'] = function
        if status!=0:
            body['status_id'] = status

        if postingFileId:
            postBodyData = {}
            postBodyData['file_id'] = postingFileId
            is_success, data = self._post_file(postBodyData)
            
        if uploaded_from:
            new_from_created_timestamp = datetime.strptime(uploaded_from, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp

        if uploaded_to:
            new_to_created_timestamp = datetime.strptime(uploaded_to, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp

        self.logger.info('========== Start searching file ==========')
        is_success, data = self._search_file(body)
        self.logger.info('========== Finished searching file ==========')
        if is_success:
            page = data['page']
            context = {
                'data': data['file_uploads'],
                'filename': filename,
                'file_id': file_id,
                'function_id': function,
                'function_list': function_list,
                'status_id': status,
                'uploaded_by': uploaded_by,
                'uploaded_from': uploaded_from,
                'uploaded_to' : uploaded_to,
                'paginator': page,
                'search_count': page['total_elements'],
                'page_range': calculate_page_range_from_page_info(page),
                'status_list_map': status_list_map
            }
        return render(request, self.template_name, context)

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

        API_Logger.post_logging(loggers=self.logger, params=body, response=data['file_uploads'],
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return is_success, data

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
        else:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Post successful"
            )
        return is_success, data
