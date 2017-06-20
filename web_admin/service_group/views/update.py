from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from web_admin import api_settings
import logging
from web_admin.utils import setup_logger
from web_admin.restful_methods import RESTfulMethods
logger = logging.getLogger(__name__)

class ServiceGroupUpdateForm(TemplateView, RESTfulMethods):
    template_name = "service_group/update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ServiceGroupUpdateForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            self.logger.info('========== Start getting service group detail ==========')

            context = super(ServiceGroupUpdateForm, self).get_context_data(**kwargs)
            service_group_id = context['ServiceGroupId']

            return self._get_service_group_detail(service_group_id)

        except:
            context = {'service_group_info': {}}
            return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating service group ==========')
        service_group_id = kwargs['ServiceGroupId']
        url = api_settings.SERVICE_GROUP_UPDATE_URL.format(service_group_id)

        name = request.POST.get('service_group_name')
        description = request.POST.get('description')

        params = {
            "service_group_name": name,
            "description": description,
        }
        data, success = self._put_method(url, "service group", logger, params)

        if success:
            self.logger.info('========== Finished updating Service Group ==========')
            request.session['service_group_update_msg'] = 'Updated service group successfully'
            return redirect('service_group:service_group_detail', ServiceGroupId=(service_group_id))
        else:
            self.logger.info("Error Updating Service Group {}".format(service_group_id))
            context = {'service_group_info': params}
            self.logger.info('========== Finish updating service group ==========')
            return render(request, 'service_group/update.html', context)


    def _get_service_group_detail(self, service_group_id):

        url = api_settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)

        data, success = self._get_method(url, "service group detail", logger, is_getting_list=False, params={})

        context = {'service_group_info': data}
        logger.info('========== Finished getting service group detail ==========')
        return context

