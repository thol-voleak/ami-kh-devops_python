from django.views.generic.base import TemplateView
from web_admin import api_settings
from web_admin.restful_helper import RestfulHelper
from web_admin.utils import calculate_page_range_from_page_info, build_logger, check_permissions
from django.shortcuts import render
import logging
from web_admin.get_header_mixins import GetHeaderMixin
from channel_gateway.api.utils  import get_service_list, get_api_list


class ListView(TemplateView, GetHeaderMixin):

    template_name = "channel-gateway-api/list.html"
    login_url = 'web:permission_denied'
    logger = logging.getLogger(__name__)

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_MANAGE_GW_API")
        self.logger = build_logger(request, __name__)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        # get undeleted services
        body_res = {
            'is_deleted': False,
            'paging': False
        }
        service_list = get_service_list(self, body_res)

        is_deleted_status_list = [{
            "value": "",
            "name": "All"
        },{
            "value": "1",
            "name": "Yes"
        },{
            "value": "0",
            "name": "No"
        }]

        http_method_list = [{
            "value": "",
            "name": "All"
        }, {
            "value": "GET",
            "name": "GET"
        }, {
            "value": "POST",
            "name": "POST"
        }, {
            "value": "PUT",
            "name": "PUT"
        }, {
            "value": "DELETE",
            "name": "DELETE"
        }]
        context.update({
            'is_deleted_status_list': is_deleted_status_list,
            'http_method_list': http_method_list,
            'service_list': service_list.get('services', [])
        })
        opening_page_index = request.GET.get('current_page_index', 1)
        api_id = request.GET.get('api_id', "")
        api_name = request.GET.get('api_name', "")
        service_id = request.GET.get('service_id', "")
        is_deleted = request.GET.get('is_deleted', "")
        http_method = request.GET.get('http_method', "")

        params = {}
        params['paging'] = True
        params['page_index'] = int(opening_page_index)
        if api_id:
            params['id'] = api_id
        if api_name:
            params['name'] = api_name
        if service_id:
            params['service_id'] = int(service_id)
        if is_deleted:
            params['is_deleted'] = True if is_deleted == '1' else False
        if http_method:
            params['http_method'] = http_method

        channel_api_list = get_api_list(self, params)
        page = channel_api_list.get('page', {})
        context.update({
            'channel_api_list': channel_api_list.get('apis', []),
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page),
            'total_result': page.get('total_elements', 0),
            "api_id": api_id,
            "api_name": api_name,
            "selected_deleted_status": is_deleted,
            "selected_http_method": http_method,
            "service_id": int(service_id) if service_id else ""
        })
        return render(request, self.template_name, context)

