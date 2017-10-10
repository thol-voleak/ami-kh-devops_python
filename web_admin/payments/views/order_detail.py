from braces.views import GroupRequiredMixin
from web_admin.restful_methods import RESTfulMethods

from django.shortcuts import render
from django.views.generic.base import TemplateView
import logging
from authentications.utils import check_permissions_by_user

logger = logging.getLogger(__name__)


class OrderDetailView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "payments/order_detail.html"
    logger = logger

    group_required = "CAN_VIEW_PAYMENT_ORDER_DETAIL"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
