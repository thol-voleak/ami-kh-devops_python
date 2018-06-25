from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.utils import calculate_page_range_from_page_info
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import render, redirect
from web_admin.restful_helper import RestfulHelper
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class AddTrust(TemplateView):
    template_name = "trust_management/add.html"
    logger = logger

    # def check_membership(self, permission):
    #     self.logger.info(
    #         "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
    #     return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddTrust, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AddTrust, self).get_context_data(**kwargs)
        context['expired_duration'] = 10
        return context

    def post(self, request, *args, **kwargs):
        context = super(AddTrust, self).get_context_data(**kwargs)
        self.logger.info('========== Start Add New Trust ==========')

        truster_user_type_id = request.POST.get('truster_user_type_id', '')
        truster_user_id = request.POST.get('truster_user_id', '')
        truster_name = request.POST.get('truster_name', '')
        trusted_user_type_id = request.POST.get('trusted_user_type_id', '')
        trusted_user_id = request.POST.get('trusted_user_id', '')
        trusted_name = request.POST.get('trusted_name', '')
        expired_unit = request.POST.get('expired_unit', '')
        expired_duration = request.POST.get('expired_duration', '')

        params = {
            "trusts": [
                {
                    "truster_user_id": truster_user_id,
                    "truster_user_type_id": truster_user_type_id,
                    "trusted_user_id": trusted_user_id,
                    "trusted_user_type_id": trusted_user_type_id,
                    "expired_unit": expired_unit,
                    "expired_duration": expired_duration
                }
            ]
        }

        # self.logger.info("Add new trust with param [{}]".format(params))

        success, data = self.add_new_trust(params)
        self.logger.info('========== Finish Adding Trust ==========')

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'New Trust Authorization successfully created'
            )
            return redirect('trust_management:list_trust')
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )

            context.update({
                "truster_user_id": truster_user_id,
                "truster_user_type_id": truster_user_type_id,
                "trusted_user_id": trusted_user_id,
                "trusted_user_type_id": trusted_user_type_id,
                "expired_unit": expired_unit,
                "expired_duration": expired_duration,
                "trusted_name": trusted_name,
                "truster_name": truster_name
            })
            return render(request, self.template_name, context)

    def add_new_trust(self, body):
        url = api_settings.ADD_TRUST
        success, status_code, status_message, data = RestfulHelper.send("POST", url, body, self.request,
                                                                        "creating trust")
        if success:
            return success, data
        else:
            return success, status_message
