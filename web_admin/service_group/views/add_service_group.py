from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods

from braces.views import GroupRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

import logging

logger = logging.getLogger(__name__)


class ServiceGroupCreate(GroupRequiredMixin, View, RESTfulMethods):
    group_required = "CAN_ADD_SERVICE_GROUP"
    login_url = 'authentications:login'
    raise_exception = False

    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ServiceGroupCreate, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        service_group_info = {
            "name": None,
            "description": None,
        }
        context = {'service_group_info': service_group_info}
        return render(request, 'service_group/add_service_group.html', context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating Service Group ==========')
        name = request.POST.get('name')
        description = request.POST.get('description')

        url = api_settings.ADD_SERVICE_GROUP_URL

        params = {
            "service_group_name": name,
            "description": description
        }
        data, success = self._post_method(url, "Service Group", logger, params)
        self.logger.info('========== Finish creating Service Group ==========')
        if success:
            request.session['add_service_group_msg'] = 'Added data successfully'
            service_group_id = data['service_group_id']
            return redirect('service_group:service_group_detail', ServiceGroupId=(service_group_id))

        else:
            service_group_info = {
                "service_group_name": name,
                "description": description,
                "failed_message": data
            }
            context = {'service_group_info': service_group_info}
            return render(request, 'service_group/add_service_group.html', context)
