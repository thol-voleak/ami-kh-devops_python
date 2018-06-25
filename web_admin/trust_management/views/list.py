from web_admin import setup_logger, api_settings
from web_admin.utils import calculate_page_range_from_page_info, build_logger, check_permissions
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import render
from web_admin.restful_helper import RestfulHelper
import logging

logger = logging.getLogger(__name__)


class ListTrust(TemplateView):
    template_name = "trust_management/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_SEARCH_TRUST")
        self.logger = build_logger(request, __name__)
        return super(ListTrust, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(ListTrust, self).get_context_data(**kwargs)
        body = {
            "paging": True,
            "page_index": 1,
            "is_deleted": False,
            "is_expired": False
        }

        trust_role = request.GET.get('trust_role')
        if trust_role and trust_role != "all":
            body['role'] = trust_role
            context['trust_role'] = trust_role
        user_id = request.GET.get('user_id')
        if user_id and user_id != '':
            body['user_id'] = user_id
            context['user_id'] = user_id
        user_type = request.GET.get('user_type')
        if user_type and user_type != "all":
            body['user_type_id'] = user_type
            context['user_type'] = user_type
        opening_page_index = request.GET.get('current_page_index')
        if opening_page_index:
            body['page_index'] = int(opening_page_index)
            context['current_page_index'] = int(opening_page_index)

        success, trusts = self.get_trust_list(body)

        if success:

            page = trusts.get("page", {})
            context.update({
                'trusts': trusts.get('token_information'),
                'paginator': page,
                'page_range': calculate_page_range_from_page_info(page)
            })
        else:
            messages.error(request, trusts)

        return render(request, self.template_name, context)

    def get_trust_list(self, body):
        url = api_settings.SEARCH_TRUST
        success, status_code, status_message, data = RestfulHelper.send("POST", url, body, self.request,
                                                                        "searching trust", log_count_field='data.token_information')
        if success:
            return success, data
        else:
            return success, status_message
