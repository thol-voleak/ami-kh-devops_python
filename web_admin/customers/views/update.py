from django.conf import settings
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.shortcuts import redirect, render
from django.contrib import messages
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UpdateView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "customer_update.html"
    logger = logger

    group_required = "CAN_EDIT_MEMBER_CUSTOMER_PROFILE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting customer detail ==========')

        customer_id = int(kwargs.get('customerId'))
        data = self.get_member_detail(customer_id=customer_id)
        data['customer_id'] = customer_id
        self.logger.info('========== Finished getting customer detail ==========')
        return data


    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating Member Customer ==========')
        customer_id = kwargs['customerId']

        body = {
            "mobile_number":request.POST.get('mobile_number'),
            "firstname":request.POST.get('firstname'),
            "lastname":request.POST.get('lastname'),
            "place_of_birth":request.POST.get('place_of_birth'),
            "citizen_card_id":request.POST.get('citizen_card_id'),
            "passport_id":request.POST.get('passport_id'),
            "citizen_card_place_of_issue":request.POST.get('citizen_card_place_of_issue'),
            "passport_place_of_issue":request.POST.get('passport_place_of_issue'),
            "permanent_address":request.POST.get('permanent_address'),
            "current_address":request.POST.get('current_address'),
            "email":request.POST.get('email'),
            "occupations":request.POST.get('occupations'),
            "nationality":request.POST.get('nationality'),
            "beneficiary":request.POST.get('beneficiary'),
            "unique_reference":request.POST.get('unique_reference')
        }

        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth = date_of_birth.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['date_of_birth'] = date_of_birth

        citizen_card_date_of_issue = request.POST.get('citizen_card_date_of_issue')
        if citizen_card_date_of_issue:
            citizen_card_date_of_issue = datetime.strptime(citizen_card_date_of_issue, "%Y-%m-%d")
            citizen_card_date_of_issue = citizen_card_date_of_issue.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['citizen_card_date_of_issue'] = citizen_card_date_of_issue

        passport_date_of_issue = request.POST.get('passport_date_of_issue')
        if passport_date_of_issue:
            passport_date_of_issue = datetime.strptime(passport_date_of_issue, "%Y-%m-%d")
            passport_date_of_issue = passport_date_of_issue.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['passport_date_of_issue'] = passport_date_of_issue


        url = api_settings.ADMIN_UPDATE_CUSTOMER.format(customer_id)
        data, success = self._put_method(url, "", logger, body, settings.GLOBAL_TIMEOUT)

        body['created_timestamp'] = request.POST.get('created_timestamp')
        body['last_updated_timestamp'] = request.POST.get('last_updated_timestamp')
        body['id'] = customer_id
        body['date_of_birth'] = date_of_birth.split('T')[0] if date_of_birth else ''
        body['citizen_card_date_of_issue'] = citizen_card_date_of_issue.split('T')[0] if citizen_card_date_of_issue else ''
        body['passport_date_of_issue'] = passport_date_of_issue.split('T')[0] if passport_date_of_issue else ''

        context = {
            'customer_info': body,
            'customer_id': customer_id
        }

        if success:
            self.logger.info('========== Finish updating Member Customer ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated profile successfully'
            )
            data = self.get_member_detail(customer_id=customer_id)
            data['customer_id'] = customer_id
            return render(request, self.template_name, data)

        elif data == 'timeout':
            messages.add_message(
                request,
                messages.ERROR,
                message='Update customer profile timeout. Please try again or contact admin.'
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message="Update customer profile fail. Please try again or contact admin."
            )
        return render(request, self.template_name, context)


    def get_member_detail(self, customer_id):
        url = api_settings.MEMBER_CUSTOMER_PATH
        body = {
            'id': customer_id
        }
        data, success = self._post_method(api_path= url,
                                          func_description="member customer detail",
                                          logger=logger,
                                          params=body)
        status = {
            True: 'Suspended',   # is_suspended == True
            False: 'Active'      # is_suspended == False
        }
        context = {'customer_info': data[0]}
        is_suspended = context['customer_info'].get('is_suspended')
        context['customer_info']['is_suspended'] = status[is_suspended]

        date_of_birth = context['customer_info']['date_of_birth']
        if date_of_birth:
            context['customer_info']['date_of_birth'] = date_of_birth.split('T')[0]

        citizen_card_date_of_issue = context['customer_info']['citizen_card_date_of_issue']
        if citizen_card_date_of_issue:
            context['customer_info']['citizen_card_date_of_issue'] = citizen_card_date_of_issue.split('T')[0]

        passport_date_of_issue = context['customer_info']['passport_date_of_issue']
        if passport_date_of_issue:
            context['customer_info']['passport_date_of_issue'] = passport_date_of_issue.split('T')[0]


        return context

