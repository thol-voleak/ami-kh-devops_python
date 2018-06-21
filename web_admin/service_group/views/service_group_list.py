from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from django.shortcuts import render

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
        self.logger.info('========== Start get Service Group List ==========')
        data, is_success = self.get_service_group_list({})
        self.logger.info('========== Finished get Service Group List ==========')
        if is_success:
            result = {'data': data.get('service_groups')}
        else:
            result = {'data': []}
        return result

    def post(self, request, *args, **kwargs):
        service_group_id = request.POST.get('service_group_id')

        body = {}
        context = {}
        if service_group_id:
            body['service_group_id'] = service_group_id
            context['service_group_id'] = service_group_id

        self.logger.info('========== Start get Service Group List ==========')
        data, is_success = self.get_service_group_list(body)
        self.logger.info('========== Finished get Service Group List ==========')
        if is_success:
            context['data'] = data.get('service_groups')
        else:
            context['data'] = []
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
            self.logger.info('========== Finished get get bank list ==========')
            for i in data.get('service_groups'):
                i['is_permission_detail'] = is_permission_detail
                i['is_permission_edit'] = is_permission_edit
                i['is_permission_delete'] = is_permission_delete

        API_Logger.get_logging(loggers=self.logger,
                               response=data,
                               status_code=status_code)
        return data, is_success


