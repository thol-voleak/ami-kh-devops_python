from django.views.generic.base import TemplateView
from web_admin import setup_logger, api_settings
from web_admin.utils import calculate_page_range_from_page_info
from django.shortcuts import render
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
import logging
from web_admin.restful_client import RestFulClient
from django.conf import settings
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class ListView(TemplateView, GetHeaderMixin):

    template_name = "channel-gateway-service/list.html"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        is_deleted_status_list = [{
            "value": "",
            "name": "All"
        },{
            "value": "0",
            "name": "Yes"
        },{
            "value": "1",
            "name": "No"
        }]
        context.update({
            'is_deleted_status_list': is_deleted_status_list
        })
        opening_page_index = request.GET.get('current_page_index', 1)
        service_id = request.GET.get('service_id', None)
        service_name = request.GET.get('service_name', None)
        is_deleted = request.GET.get('is_deleted', None)

        params = {}
        params['paging'] = True
        params['page_index'] = int(opening_page_index)
        if service_id:
            params['id'] = service_id
        if service_name:
            params['name'] = service_name
        if is_deleted:
            params['is_deleted'] = True if is_deleted == '0' else False

        self.logger.info('========== Start get channel gateway service list ==========')
        channel_service_list = self.get_service_list(params)
        self.logger.info('========== Finish get channel gateway service list ==========')
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

        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=params,
                                                                        timeout=settings.GLOBAL_TIMEOUT)
        if data is None:
            data = {}
            data['services'] = []

        API_Logger.post_logging(loggers=self.logger, params=params, response=data['services'],
                                status_code=status_code, is_getting_list=True)
        return data
