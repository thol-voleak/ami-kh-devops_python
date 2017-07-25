from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods

from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView

import logging
logger = logging.getLogger(__name__)


class ServiceGroupDetailForm(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_SERVICE_GROUP"
    login_url = 'web:web-index'
    raise_exception = False

    template_name = "service_group/detail.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ServiceGroupDetailForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            self.logger.info('========== Start getting service group detail ==========')

            context = super(ServiceGroupDetailForm, self).get_context_data(**kwargs)
            service_group_id = context['ServiceGroupId']

            return self._get_service_group_detail(service_group_id)

        except:
            context = {'service_group_info': {}}
            return context


    def _get_service_group_detail(self, service_group_id):
        url = api_settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)
        data, success = self._get_method(url, "service group detail", logger)

        if success:
            context = {'service_group_info': data,
                       'add_service_group_msg': self.request.session.pop('add_service_group_msg', None),
                       'service_group_update_msg': self.request.session.pop('service_group_update_msg', None)}
            self.logger.info('========== Finished getting service group detail ==========')
            return context
        else:
            self.logger.info("Error Getting System User Detail.")
            context = {'service_group_info': data}
            self.logger.info('========== Finished getting service group detail ==========')
            return context


