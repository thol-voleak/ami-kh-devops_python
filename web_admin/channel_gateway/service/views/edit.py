from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
from web_admin import setup_logger, api_settings
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render, redirect
from django.contrib import messages
import logging
from web_admin.restful_helper import RestfulHelper
from web_admin.utils import check_permissions, build_logger

logger = logging.getLogger(__name__)


class EditView(TemplateView):
    template_name = "channel-gateway-service/edit.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_EDIT_GW_SERVICE")
        self.logger = build_logger(request, __name__)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        services_id = int(kwargs['id'])
        service  = self.get_service_detail(services_id)
        context = {
            "form" : service
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        service_id = int(kwargs['id'])
        url = api_settings.EDIT_CHANNEL_SERVICE.format(service_id=service_id)
        form = request.POST
        params = {
            'name': form['name'],
            'location': form['location']
        }

        if form.get('timeout'):
            params['timeout'] = int(form['timeout'])

        if form.get('max_per_route'):
            params['max_per_route'] = int(form['max_per_route'])

        if form.get('max_total_connection'):
            params['max_total_connection'] = int(form['max_total_connection'])

        is_success, status_code, status_message, data = RestfulHelper.send("PUT", url, params, self.request, "Update Service")

        if is_success:
            messages.add_message(request, messages.SUCCESS, 'Service has been edited')
            return redirect('channel_gateway_service:list')
        else:
            messages.add_message(request, messages.ERROR, status_message)
            return render(request, self.template_name, context={'form': form})

    
    def get_service_detail(self, services_id):
        url = api_settings.GET_CHANNEL_SERVICE
        params = {
            "id": services_id
        }
        is_success, status_code, status_message, data = RestfulHelper.send("POST", url, params, self.request, "get service detail")
        if data:
            return data["services"][0]
        else:
            return None

        
        