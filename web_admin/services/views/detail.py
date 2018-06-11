from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class ServiceDetailForm(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "services/service_detail.html"
    logger=logger

    group_required = "CAN_VIEW_SERVICE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))

        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ServiceDetailForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailForm, self).get_context_data(**kwargs)
        service_id = context['ServiceId']
        return self._get_service_detail(service_id)

    def post(self, request, **kwargs):
        context = super(ServiceDetailForm, self).get_context_data(**kwargs)
        service_id = context['ServiceId']
        context = self._get_service_detail(service_id)
        return JsonResponse({"service": context.get('service_info')})

    def _get_service_detail(self, service_id):

        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        data, success = self._get_method(url, "service detail", logger)
        if success:
            service_group_id = data['service_group_id']
            service_group_name = self._get_service_group_name(service_group_id)
            data['service_group_name'] = service_group_name

        context = {'service_info': data,
                   'can_edit_service': self.check_membership(['CAN_EDIT_SERVICE']),
                   'add_service_msg': self.request.session.pop('add_service_msg', None),
                   'update_service_msg': self.request.session.pop('update_service_msg', None)}
        return context

    def _get_service_group_name(self, service_group_id):
        url = api_settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)
        data, success = self._get_method(api_path=url)
        if success:
            return data['service_group_name']
        else:
            return None
