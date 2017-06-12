import logging

from django.views.generic.base import TemplateView
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from django.contrib import messages
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

class ServiceGroupDeleteForm(TemplateView, RESTfulMethods):
    template_name = "service_group/delete.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting service group delete detail ==========')

            context = super(ServiceGroupDeleteForm, self).get_context_data(**kwargs)
            service_group_id = context['ServiceGroupId']

            return self._get_service_group_detail(service_group_id)

        except:
            context = {'service_group_info': {}}
            return context


    def _get_service_group_detail(self, service_group_id):
        url = api_settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)
        data, success = self._get_method(url, "service group detail", logger)

        if success:
            context = {'service_group_info': data}
            logger.info('========== Finished getting service group delete detail ==========')
            return context
        else:
            logger.info("Error Getting System User Delete Detail.")
            context = {'service_group_info': data}
            logger.info('========== Finished getting service group delete detail ==========')
            return context


    def post(self, request, *args, **kwargs):
        logger.info('========== Start deleting service group ==========')

        context = super(ServiceGroupDeleteForm, self).get_context_data(**kwargs)
        service_group_id = context['ServiceGroupId']
        api_path = api_settings.DELETE_SERVICE_GROUP_URL.format(service_group_id)

        # Do Request
        data, status = self._delete_method(
            api_path=api_path,
            func_description="Service Group Delete",
            logger=logger
        )
        logger.info('========== Finish deleting service group ==========')
        if status:
            messages.add_message(request, messages.SUCCESS, 'Deleted data successfully')
            return redirect('service_group:service_group_list')
        else:
            logger.info("Error deleting service group {}".format(service_group_id))
            return redirect('service_group:service_group_delete', ServiceGroupId=(service_group_id))



