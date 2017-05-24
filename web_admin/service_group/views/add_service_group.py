from django.shortcuts import render, redirect
from django.views import View
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods
import logging

logger = logging.getLogger(__name__)


class ServiceGroupCreate(View, RESTfulMethods):
    def get(self, request, *args, **kwargs):
        service_group_info = {
            "name": None,
            "description": None,
        }
        context = {'service_group_info': service_group_info}
        return render(request, 'service_group/add_service_group.html', context)

    def post(self, request, *args, **kwargs):
        logger.info('========== Start creating Service Group ==========')
        name = request.POST.get('name')
        description = request.POST.get('description')

        url = api_settings.ADD_SERVICE_GROUP_URL

        params = {
            "service_group_name": name,
            "description": description
        }
        data, success = self._post_method(url, "Service Group", logger, params)
        logger.info('========== Finish creating Service Group ==========')
        if success:
            request.session['add_service_group_msg'] = 'Added data successfully'
            service_group_id = data['service_group_id']
            return redirect('service_group:service_group_detail', ServiceGroupId=(service_group_id))

        else:
            service_group_info = {
                "service_group_name": name,
                "description": description
            }
            context = {'service_group_info': service_group_info}
            return render(request, 'service_group/add_service_group.html', context)

