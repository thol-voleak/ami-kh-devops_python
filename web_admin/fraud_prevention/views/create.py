import logging

from braces.views import GroupRequiredMixin

from web_admin import setup_logger
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user


logger = logging.getLogger(__name__)


class FPCreateView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = 'fraud_prevention/create.html'
    logger = logger

    group_required = "CAN_VIEW_CLIENTS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(FPCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})
