from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods

from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)


class ServiceGroupDeleteForm(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_DELETE_SERVICE_GROUP"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "service_group/delete.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ServiceGroupDeleteForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            self.logger.info('========== Start getting service group delete detail ==========')

            context = super(ServiceGroupDeleteForm, self).get_context_data(**kwargs)
            service_group_id = context['ServiceGroupId']

            return self._get_service_group_detail(service_group_id)

        except:
            context = {'service_group_info': {}}
            return context


    def _get_service_group_detail(self, service_group_id):
        url = api_settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)
        data, success = self._get_method(url, "service group detail", logger)

        if success:
            context = {'service_group_info': data}
            self.logger.info('========== Finished getting service group delete detail ==========')
            return context
        else:
            self.logger.info("Error Getting System User Delete Detail.")
            context = {'service_group_info': data}
            self.logger.info('========== Finished getting service group delete detail ==========')
            return context


    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting service group ==========')

        context = super(ServiceGroupDeleteForm, self).get_context_data(**kwargs)
        service_group_id = context['ServiceGroupId']
        api_path = api_settings.DELETE_SERVICE_GROUP_URL.format(service_group_id)

        # Do Request
        data, status = self._delete_method(
            api_path=api_path,
            func_description="Service Group Delete",
            logger=logger
        )
        self.logger.info('========== Finish deleting service group ==========')
        if status:
            messages.add_message(request, messages.SUCCESS, 'Deleted data successfully')
            return redirect('service_group:service_group_list')
        else:
            messages.add_message(request, messages.ERROR, data)
            self.logger.info("Error deleting service group {}".format(service_group_id))
            return redirect('service_group:service_group_delete', ServiceGroupId=(service_group_id))



