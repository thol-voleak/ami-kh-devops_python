from django.views.generic.base import TemplateView
from authentications.utils import check_permissions_by_user
from web_admin import api_settings
from web_admin.restful_helper import RestfulHelper
from web_admin.utils import calculate_page_range_from_page_info, build_logger, check_permissions
from django.shortcuts import render
import logging
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin


class ListView(TemplateView, GetHeaderMixin):

    template_name = "channel-gateway-service/list.html"
    logger = logging.getLogger(__name__)

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_MANAGE_GW_SERVICE")
        self.logger = build_logger(request, __name__)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        is_deleted_status_list = [{
            "value": "0",
            "name": "No"
        },{
            "value": "1",
            "name": "Yes"
        },{
            "value": "",
            "name": "All"
        }]
        context.update({
            'is_deleted_status_list': is_deleted_status_list
        })
        opening_page_index = request.GET.get('current_page_index', 1)
        service_id = request.GET.get('service_id', "")
        service_name = request.GET.get('service_name', "")
        is_deleted = request.GET.get('is_deleted', "0")

        params = {}
        params['paging'] = True
        params['page_index'] = int(opening_page_index)
        if service_id:
            params['id'] = service_id
        if service_name:
            params['name'] = service_name
        if is_deleted:
            params['is_deleted'] = True if is_deleted == '1' else False

        channel_service_list = self.get_service_list(params)
        page = channel_service_list.get('page', {})
        context.update({
            'channel_service_list': channel_service_list.get('services', []),
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page),
            'total_result': page.get('total_elements', 0),
            "service_id": service_id,
            "selected_deleted_status": is_deleted,
            "service_name": service_name
        })
        return render(request, self.template_name, context)

    def get_service_list(self, params):
        api_path = api_settings.GET_CHANNEL_SERVICE

        success, status_code, status_message, data = RestfulHelper.send("POST", api_path, params, self.request, "get service list", "data.services")
        if data is None:
            data = {}
            data['services'] = []
        return data
