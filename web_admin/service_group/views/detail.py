from django.views.generic.base import TemplateView
from web_admin import api_settings
import logging
from web_admin.utils import setup_logger
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class ServiceGroupDetailForm(TemplateView, RESTfulMethods):
    template_name = "service_group/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
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


