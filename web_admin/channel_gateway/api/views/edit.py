from web_admin.utils import check_permissions, build_logger
from django.views.generic.base import TemplateView
from web_admin import setup_logger, api_settings
from web_admin.restful_helper import RestfulHelper
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from channel_gateway.api.utils import get_api_detail, get_service_list
import logging

logger = logging.getLogger(__name__)


class EditView(TemplateView, GetHeaderMixin):
    template_name = "channel-gateway-api/edit.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_EDIT_GW_API")
        self.logger = build_logger(request, __name__)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        api_id = int(kwargs['id'])
        body_res = {
            'is_deleted': False,
            'paging': False
        }
        service_list = get_service_list(self, body_res)
        api = get_api_detail(self, api_id)
        context = {
            "service_list":service_list,
            "form": api
        }
        return render(request, self.template_name, context)
    def post (self, request, *args, **kwargs):
        api_id = int(kwargs['id'])
        url = api_settings.EDIT_CHANNEL_API.format(api_id=api_id)
        form = request.POST
        params = {}

        if form.get('name'):
            params['name'] = form['name']

        if form.get('http_method'):
            params['http_method'] = form['http_method']

        if form.get('pattern'):
            params['pattern'] = form['pattern']

        if form.get('service_id'):
            params['service_id'] = int(form['service_id'])

        if form.get('require_access_token'):
            params['is_required_access_token'] = True if form['require_access_token'] == '1' else False

        success, status_code, status_message, data = RestfulHelper.send("PUT", url, params, self.request, "Update API")

        if success:
            messages.add_message(request, messages.SUCCESS, 'API has been edited')
            return redirect('channel_gateway_api:list')
        else:
            body_res = {
                'is_deleted': False,
                'paging': False
            }
            service_list = get_service_list(self, body_res)
            messages.add_message(request, messages.ERROR, status_message)
            return render(request, self.template_name, context={'form': form, 'service_list': service_list})