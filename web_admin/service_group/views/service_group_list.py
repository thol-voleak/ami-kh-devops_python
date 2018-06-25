from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from datetime import date, timedelta, datetime

from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.utils import calculate_page_range_from_page_info, make_download_file, export_file
from django.shortcuts import render
from django.contrib import messages

from braces.views import GroupRequiredMixin

from django.views.generic.base import TemplateView

import logging
logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_LIST_SERVICE_GROUP"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "service_group/service_group_list.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.logger.info('========== Start get Service Group List ==========')

        self.initSearchDateTime(context)

        body = {
            'is_deleted': False,
            'paging': True,
            'page_index': 1
        }

        data, is_success = self.get_service_group_list(body)
        self.logger.info('========== Finished get Service Group List ==========')
        if is_success:
            page = data.get("page", {})
            context.update({
                'data': data.get('service_groups'),
                'paginator': page,
                'page_range': calculate_page_range_from_page_info(page),
                'search_count': page.get('total_elements', 0),
                'is_show_export': check_permissions_by_user(self.request.user, 'CAN_EXPORT_SERVICE_GROUP')
            })
        else:
            context.update({
                'data': [],
                'is_show_export': True
            })
        return context

    def post(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        self.logger.info('========== Start {} service groups list =========='.format("downloading" if 'download' in request.POST else "searching"))

        service_group_id = request.POST.get('service_group_id')
        service_group_name = request.POST.get('service_group_name')
        created_from_date = request.POST.get('created_from_date')
        created_to_date = request.POST.get('created_to_date')
        created_from_time = request.POST.get('created_from_time')
        created_to_time = request.POST.get('created_to_time')
        modified_from_date = request.POST.get('modified_from_date')
        modified_to_date = request.POST.get('modified_to_date')
        modified_from_time = request.POST.get('modified_from_time')
        modified_to_time = request.POST.get('modified_to_time')
        opening_page_index = request.POST.get('current_page_index')

        body = {'is_deleted': False}

        if service_group_id:
            body['service_group_id'] = service_group_id
        if service_group_name:
            body['service_group_name'] = service_group_name
        if created_from_date:
            body['from_created_timestamp'] = self.convertStringToDateTime(created_from_date, created_from_time)
        if created_to_date:
            body['to_created_timestamp'] = self.convertStringToDateTime(created_to_date, created_to_time)
        if modified_from_date:
            body['from_last_updated_timestamp'] = self.convertStringToDateTime(modified_from_date, modified_from_time)
        if modified_to_date:
            body['to_last_updated_timestamp'] = self.convertStringToDateTime(modified_to_date, modified_to_time)

        if 'download' in request.POST:
            file_type = request.POST.get('export-type')
            body['file_type'] = file_type
            body['row_number'] = 5000
            is_success, data = export_file(self, body=body, url_download=api_settings.SERVICE_GROUP_LIST_PATH, api_logger=API_Logger)
            if is_success:
                response = make_download_file(data, file_type)
                self.logger.info('========== Finish exporting payment service ==========')
                return response
        else:
            body['paging'] = True
            body['page_index'] = int(opening_page_index)
            data, is_success = self.get_service_group_list(body)
            page = data.get("page", {})

            context.update({
                'service_group_id': service_group_id,
                'service_group_name': service_group_name,
                'created_from_date': created_from_date,
                'created_to_date': created_to_date,
                'created_from_time': created_from_time,
                'created_to_time': created_to_time,
                'modified_from_date': modified_from_date,
                'modified_to_date': modified_to_date,
                'modified_from_time': modified_from_time,
                'modified_to_time': modified_to_time,
                'search_count': page.get('total_elements', 0),
                'data': data['service_groups'],
                'paginator': page,
                'page_range': calculate_page_range_from_page_info(page),
                'is_show_export': check_permissions_by_user(self.request.user, 'CAN_EXPORT_SERVICE_GROUP')
            })

            self.logger.info('========== Finish searching service groups list ==========')
            return render(request, self.template_name, context)

    def get_service_group_list(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.SERVICE_GROUP_LIST_PATH,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)
        is_permission_detail = check_permissions_by_user(self.request.user, 'CAN_VIEW_SERVICE_GROUP')
        is_permission_edit = check_permissions_by_user(self.request.user, 'CAN_EDIT_SERVICE_GROUP')
        is_permission_delete = check_permissions_by_user(self.request.user, 'CAN_DELETE_SERVICE_GROUP')

        if is_success:
            self.logger.info('Finished get service group list')
            for i in data.get('service_groups'):
                i['is_permission_detail'] = is_permission_detail
                i['is_permission_edit'] = is_permission_edit
                i['is_permission_delete'] = is_permission_delete
        else:
            if status_code == "Timeout":
                self.logger.error('Search service group list request timeout')
                status_message = 'Search timeout, please try again or contact technical support'

            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )

        API_Logger.get_logging(loggers=self.logger,
                               response=data,
                               status_code=status_code)
        return data, is_success

    def initSearchDateTime(self, context):
        today = date.today()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)
        context['created_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['created_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['created_from_time'] = "00:00:00"
        context['created_to_time'] = "00:00:00"
        context['modified_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['modified_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['modified_from_time'] = "00:00:00"
        context['modified_to_time'] = "00:00:00"


    def convertStringToDateTime(self, date_str, time_str):
        _date = datetime.strptime(date_str, "%Y-%m-%d")
        time_split = time_str.split(":")
        if len(time_split) == 3:
            return _date.replace(hour = int(time_str.split(":")[0]),
                                 minute = int(time_str.split(":")[1]),
                                 second = int(time_str.split(":")[2])).strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return _date.replace(hour=int(time_str.split(":")[0]),
                                        minute=int(time_str.split(":")[1]),
                                        second= 0).strftime('%Y-%m-%dT%H:%M:%SZ')



