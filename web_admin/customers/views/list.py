from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView
from django.shortcuts import render
from braces.views import GroupRequiredMixin

import logging

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_SEARCH_CUSTOMER"
    login_url = 'authentications:login'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'member_customer_list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.logger.info('========== Start searching Customer ==========')
        url = api_settings.MEMBER_CUSTOMER_PATH
        search = request.GET.get('search')
        if search is None:
            data = {}
        else:
            if search == '':
                params = {}
            else:
                params = {"mobile_number": search}
            data, success = self._post_method(api_path= url,
                                              func_description="search member customer",
                                              logger=logger,
                                              params=params)

        is_permision_detail = check_permissions_by_user(self.request.user, 'CAN_VIEW_DETAIL_MEMBER_CUSTOMER_PROFILE')
        is_permision_sof_bank = check_permissions_by_user(self.request.user, 'CAN_VIEW_BANK_SOF_CUSTOMER_PROFILE')
        is_permision_identity = check_permissions_by_user(self.request.user, 'CAN_VIEW_IDENTITY_CUSTOMER')
        is_permision_suspend = check_permissions_by_user(self.request.user, 'CAN_SUSPEND_CUSTOMER')

        for i in data:
            i['is_permission_detail'] = is_permision_detail
            i['is_permission_sof_bank'] = is_permision_sof_bank
            i['is_permission_identity'] = is_permision_identity
            i['is_permission_suspend'] = is_permision_suspend

        context['search_count'] = len(data)
        context['data'] = data
        self.logger.info('========== Finished searching Customer ==========')
        return render(request, 'member_customer_list.html', context)

