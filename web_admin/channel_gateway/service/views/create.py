from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_helper import RestfulHelper
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render, redirect
from django.contrib import messages
import logging

from web_admin.utils import check_permissions, build_logger

logger = logging.getLogger(__name__)


class CreateView(TemplateView, GetHeaderMixin):
    template_name = "channel-gateway-service/create.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_CREATE_GW_SERVICE")
        self.logger = build_logger(request, __name__)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request):
        form = request.POST
        params = {}

        if form.get('name'):
            params['name'] = form['name']

        if form.get('location'):
            params['location'] = form['location']

        if form.get('timeout'):
            params['timeout'] = int(form['timeout'])

        if form.get('max_per_route'):
            params['max_per_route'] = int(form['max_per_route'])

        if form.get('max_total_connection'):
            params['max_total_connection'] = int(form['max_total_connection'])

        success, status_code, message, data = self.add_channel_service(params)

        if success:
            messages.add_message(request, messages.SUCCESS, 'New service has been created')
            return redirect('channel_gateway_service:list')
        else:
            messages.add_message(request, messages.ERROR, message)
            return render(request, self.template_name, context={'form': form})

    def add_channel_service(self, params):
        success, status_code, message, data = RestfulHelper.send("POST", api_settings.CHANNEL_SERVICE, params, self.request, "Adding new channel service")
        return success, status_code, message, data