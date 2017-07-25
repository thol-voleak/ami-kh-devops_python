import logging
from django.views.generic.base import TemplateView
from django.shortcuts import render
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.utils import setup_logger
from web_admin.api_settings import CUSTOMER_IDENTITIES_LIST
from braces.views import GroupRequiredMixin

logger = logging.getLogger(__name__)


class CustomerIdentitiesListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_IDENTITY_CUSTOMER"
    login_url = 'web:web-index'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'member_customer_identities.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CustomerIdentitiesListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args,**kwargs):
        self.logger.info('========== Start getting member customer identities ==========')
        customer_id = int(kwargs.get('customerId'))
        url = CUSTOMER_IDENTITIES_LIST
        param = {'customer_id':customer_id}
        data, success = self._post_method(api_path=url,
                                          func_description="member customer identities",
                                          logger=logger,
                                          params=param)

        is_permision_reset_password = check_permissions_by_user(self.request.user, 'CAN_RESETPASSWORD_MEMBER_CUSTOMER')
        for i in data:
            i['is_permision_reset_password'] = is_permision_reset_password

        context = {'customer_id':customer_id,'data': data}
        self.logger.info('========== Finished getting member customer identities ==========')
        return render(request, self.template_name, context)
