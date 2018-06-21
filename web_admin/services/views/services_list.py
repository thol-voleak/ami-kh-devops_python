from web_admin.api_settings import SEARCH_SERVICE, SERVICE_GROUP_LIST_URL
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_helper import RestfulHelper
from web_admin.api_logger import API_Logger
from django.shortcuts import render
from web_admin.utils import calculate_page_range_from_page_info, make_download_file, export_file
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView

import logging


logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_MANAGE_SERVICE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "services/services_list.html"
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
        context = {}
        params = {'paging': True, 'page_index': 1}

        # Search with default status is activated - '1'
        params['status'] = 1

        success, data = self.get_services_list(params)

        service_list = data.get('services') if success else []
        page = data.get("page", {})
        context['search_count'] = page.get('total_elements', 0)
        service_group_list = self.get_service_group_list()
        service_groups = []
        for i in service_list:
            for j in service_group_list:
                if i['service_group_id'] == j['service_group_id']:
                    i['service_group_name'] = j['service_group_name']
                    break

        for i in service_group_list:
            service_groups.append({'id': str(i['service_group_id']), 'name': i['service_group_name']})

        permissions = {
            'CAN_VIEW_SERVICE': check_permissions_by_user(self.request.user, 'CAN_VIEW_SERVICE'),
            'CAN_EDIT_SERVICE': check_permissions_by_user(self.request.user, 'CAN_EDIT_SERVICE'),
            'CAN_EDIT_COMMAND_SERVICE': check_permissions_by_user(self.request.user, 'CAN_EDIT_COMMAND_SERVICE'),
            'CAN_DELETE_SERVICE': check_permissions_by_user(self.request.user, 'CAN_DELETE_SERVICE'),
            'CAN_ADD_SERVICE': check_permissions_by_user(self.request.user, 'CAN_ADD_SERVICE')
        }

        context['paginator'] = page
        context['page_range'] = calculate_page_range_from_page_info(page)
        context['data'] = service_list
        context['service_groups'] = service_groups
        context['permissions'] = permissions
        return context

    def post(self, request, *args, **kwargs):
        params = {}
        context = {}

        name = request.POST.get('name')
        id = request.POST.get('id')
        currency = request.POST.get('currency')
        group = request.POST.get('group')
        status = request.POST.get('status')
        opening_page_index = request.POST.get('current_page_index')

        if id:
            context['id'] = id
            params['id'] = id
        if name:
            context['name'] = name
            params['service_name'] = name
        if currency:
            context['currency'] = currency
            params['currency'] = currency
        if group:
            context['group'] = group
            params['service_group_id'] = group
        if not status:
            params['status'] = 1
        else:
            context['status'] = status
        if status in ['0', '1']:
            params['status'] = int(status)

        if 'download' in request.POST:
            self.logger.info('========== Start exporting payment service ==========')
            file_type = request.POST.get('export-type')
            params['file_type'] = file_type
            params['row_number'] = 5000
            is_success, data = export_file(self, body=params, url_download=SEARCH_SERVICE, api_logger=API_Logger)
            if is_success:
                response = make_download_file(data, file_type)
                self.logger.info('========== Finish exporting payment service ==========')
                return response
        else:
            params['paging']= True
            if opening_page_index:
                params['page_index'] = int(opening_page_index)
                context['current_page_index'] = int(opening_page_index)
            else:
                params['page_index']= 1

            success, data = self.get_services_list(params)
            service_list = data.get('services') if success else []
            page = data.get("page", {})
            context['search_count'] = page.get('total_elements', 0)
            service_group_list = self.get_service_group_list()
            service_groups = []
            for i in service_list:
                for j in service_group_list:
                    if i['service_group_id'] == j['service_group_id']:
                        i['service_group_name'] = j['service_group_name']
                        break

            for i in service_group_list:
                service_groups.append({'id': str(i['service_group_id']), 'name': i['service_group_name']})

            permissions = {
                'CAN_VIEW_SERVICE': check_permissions_by_user(self.request.user, 'CAN_VIEW_SERVICE'),
                'CAN_EDIT_SERVICE': check_permissions_by_user(self.request.user, 'CAN_EDIT_SERVICE'),
                'CAN_EDIT_COMMAND_SERVICE': check_permissions_by_user(self.request.user, 'CAN_EDIT_COMMAND_SERVICE'),
                'CAN_DELETE_SERVICE': check_permissions_by_user(self.request.user, 'CAN_DELETE_SERVICE'),
                'CAN_ADD_SERVICE': check_permissions_by_user(self.request.user, 'CAN_ADD_SERVICE')
            }

            context['paginator'] = page
            context['page_range'] = calculate_page_range_from_page_info(page)
            context['data'] = service_list
            context['service_groups'] = service_groups
            context['permissions'] = permissions
            return render(request, self.template_name, context)

    def get_services_list(self, params):
        url = SEARCH_SERVICE
        success, status_code, status_message, data = RestfulHelper.send("POST", url, params, self.request, "searching service", "data.services")
        return success, data

    def get_service_group_list(self):
        url = SERVICE_GROUP_LIST_URL
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting service groups", "data")
        is_permission_detail = check_permissions_by_user(self.request.user, 'CAN_VIEW_SERVICE_GROUP')
        is_permission_edit = check_permissions_by_user(self.request.user, 'CAN_EDIT_SERVICE_GROUP')
        is_permission_delete = check_permissions_by_user(self.request.user, 'CAN_DELETE_SERVICE_GROUP')

        if success:
            for i in data:
                i['is_permission_detail'] = is_permission_detail
                i['is_permission_edit'] = is_permission_edit
                i['is_permission_delete'] = is_permission_delete
        return data
