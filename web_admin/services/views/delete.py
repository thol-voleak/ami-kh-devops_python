import logging

from django.views.generic.base import TemplateView
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
from django.contrib import messages
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

class ServiceDeleteForm(TemplateView, RESTfulMethods):
    template_name = "services/delete.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting service delete detail ==========')

        context = super(ServiceDeleteForm, self).get_context_data(**kwargs)
        service_id = context['ServiceId']

        return self._get_service_detail(service_id)


    def _get_service_detail(self, service_id):
        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        data, success = self._get_method(url, "service detail", logger)

        if success:
            context = {'service_info': data}
            logger.info('========== Finished getting service delete detail ==========')
            return context
        else:
            logger.info("Error Getting Service Delete Detail.")
            context = {'service_info': data}
            logger.info('========== Finished getting service delete detail ==========')
            return context


    def post(self, request, *args, **kwargs):
        logger.info('========== Start deleting service ==========')

        context = super(ServiceDeleteForm, self).get_context_data(**kwargs)
        service_id = context['ServiceId']
        api_path = api_settings.SERVICE_DELETE_URL.format(service_id)

        data, status = self._delete_method(
            api_path=api_path,
            func_description="Service Delete",
            logger=logger
        )
        logger.info('========== Finish deleting service ==========')
        if status:
            messages.add_message(request, messages.SUCCESS, 'Deleted Data Successfully')
            return redirect('services:services_list')
        else:
            messages.add_message(request, messages.ERROR, data)
            logger.info("Error deleting service {}".format(service_id))
            return redirect('services:delete_service', ServiceId=(service_id))



