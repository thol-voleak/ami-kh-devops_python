from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.utils import calculate_page_range_from_page_info
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import render, redirect
from web_admin.restful_helper import RestfulHelper
from datetime import date
import logging

logger = logging.getLogger(__name__)


class TrustList(TemplateView):
    template_name = "trust_management/list.html"
    logger = logger

    # def check_membership(self, permission):
    #     self.logger.info(
    #         "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
    #     return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(TrustList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(TrustList, self).get_context_data(**kwargs)
        body = {
            "paging": True,
            "page_index": 1
            # "is_deleted": False
        }

        trust_role = request.GET.get('trust_role')
        # if trust_role ====== if trust_role != None, != 0, != (), != [], != {}, defined
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

    # def post(self, request, *args, **kwargs):
    #     context = super(TrustList, self).get_context_data(**kwargs)
    #     opening_page_index = request.POST.get('current_page_index')
    #
    #     body = {}
    #     body['paging'] = True
    #     body['page_index'] = int(opening_page_index)
    #
    #     shop_types = self.get_shop_type(body)
    #     page = shop_types.get("page", {})
    #
    #     context.update({
    #         'shop_types': shop_types['shop_types'],
    #         'paginator': page,
    #         'page_range': calculate_page_range_from_page_info(page)
    #     })
    #     return render(request, self.template_name, context)
