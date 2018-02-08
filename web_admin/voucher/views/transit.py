from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import redirect
import logging
from braces.views import GroupRequiredMixin
from django.contrib import messages

logger = logging.getLogger(__name__)

class Transit(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    group_required = "CAN_CREATE_VOUCHER_ACTION"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(Transit, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.request.session['Add_New_Voucher'] = 'Add New Voucher'
        return redirect('balance_adjustment:balance_adjustment_create')
