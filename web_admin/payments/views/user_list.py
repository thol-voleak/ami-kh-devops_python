from braces.views import GroupRequiredMixin

from web_admin import setup_logger
from django.shortcuts import render
from django.views.generic.base import TemplateView
import logging
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import GET_USER_BY_PHONE_URL
from authentications.utils import check_permissions_by_user, get_correlation_id_from_username
from web_admin.api_logger import API_Logger
from django.http import JsonResponse, HttpResponse
from web_admin.utils import calculate_page_range_from_page_info

logger = logging.getLogger(__name__)


class UserList(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "payments/user_list.html"
    logger = logger

    group_required = "CAN_VIEW_PAYMENT_ORDER_DETAIL"
    login_url = 'web:permission_denied'
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UserList, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting user list ==========')
        context = super(UserList, self).get_context_data(**kwargs)
        mobile_number = request.GET.get('mobile_number')
        opening_page_index = request.GET.get('current_page_index')
        body = {'paging': True, 'page_index': int(opening_page_index), 'mobile_number': mobile_number}

        is_success, status_code, status_message, data = self.search_user_list(body=body)
        if is_success:
            page = data.get("page", {})
            user_list = data['users']
            total_elements = page.get('total_elements', 0)
            if total_elements == 0:
                return JsonResponse({
                    'no_record': 'true'
                })
            elif total_elements == 1:
                user = data['users'][0]
                return JsonResponse(user)
            else:
                page_range = calculate_page_range_from_page_info(page)
                context.update({'user_list': user_list,
                           'paginator': page,
                           'search_count': page.get('total_elements', 0),
                           'page_range': page_range
                           })

            self.logger.info('========== End getting user list ==========')
            return render(request, "payments/user_list.html", context)
        else:
            if status_code == 'Timeout':
                return HttpResponse(status=504)
            return HttpResponse(status=500)

    def search_user_list(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=GET_USER_BY_PHONE_URL,
                                                           headers=self._get_headers(),
                                                           loggers=self.logger,
                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, response=data,
                                status_code=status_code, is_getting_list=False)

        return is_success, status_code, status_message, data