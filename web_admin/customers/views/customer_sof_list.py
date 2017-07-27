from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods

from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin

import logging

logger = logging.getLogger(__name__)


class CustomerSOFListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_BANK_SOF_CUSTOMER_PROFILE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'member_customer_sof_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CustomerSOFListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting customer sof bank ==========')

        customer_id = int(kwargs.get('customerId'))

        url = settings.DOMAIN_NAMES + "report/" + api_settings.API_VERSION + "/banks/sofs"
        self.logger.info('API-Path: {};'.format(url))
        param = {
            "user_id": customer_id
        }
        data, success = self._post_method(api_path=url,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params=param)

        context = {'data': data}
        self.logger.info('========== Finished searching customer sof ==========')
        return render(request, self.template_name, context)
