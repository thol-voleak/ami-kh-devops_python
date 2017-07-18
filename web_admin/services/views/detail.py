from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
import logging
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class ServiceDetailForm(TemplateView, RESTfulMethods):
    template_name = "services/service_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceDetailForm, self).get_context_data(**kwargs)
        service_id = context['ServiceId']
        return self._get_service_detail(service_id)

    def _get_service_detail(self, service_id):

        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        data, success = self._get_method(url, "service detail", logger)
        if success:
            service_group_id = data['service_group_id']
            service_group_name = self._get_service_group_name(service_group_id)
            data['service_group_name'] = service_group_name

        context = {'service_info': data,
                   'add_service_msg': self.request.session.pop('add_service_msg', None),
                   'update_service_msg': self.request.session.pop('update_service_msg', None)}
        return context

    def _get_service_group_name(self, service_group_id):
        url = api_settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)
        data, success = self._get_method(url, "service group detail", logger)
        if success:
            return data['service_group_name']
        else:
            return None
