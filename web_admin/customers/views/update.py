from django.conf import settings
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from django.shortcuts import redirect, render
from django.contrib import messages
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UpdateView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "customer_update.html"
    logger = logger

    group_required = "CAN_EDIT_MEMBER_CUSTOMER_PROFILE"
    login_url = 'web:permission_denied'
    raise_exception = False
    status = {
            True: 'Suspended',   # is_suspended == True
            False: 'Active'      # is_suspended == False
        }

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
        context = self.get_member_detail(customer_id=customer_id)
        self.logger.info('========== Finished getting customer detail ==========')

        return context


    def post(self, request, *args, **kwargs):
        body = {}
        self.logger.info('========== Start updating Member Customer ==========')
        customer_id = kwargs['customerId']

        # personal detail section 
        firstname = request.POST.get('firstname')
        middle_name = request.POST.get('middle_name')
        lastname = request.POST.get('lastname')
        place_of_birth = request.POST.get('place_of_birth')
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            date_of_birth2 = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth2 = date_of_birth2.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['date_of_birth'] = date_of_birth2
        gender = request.POST.get('gender')
        occupations = request.POST.get('occupations')
        nationality = request.POST.get('nationality')
        beneficiary = request.POST.get('beneficiary')
        unique_reference = request.POST.get('unique_reference')
        citizen_card_id = request.POST.get('citizen_card_id')
        passport_id = request.POST.get('passport_id')
        tax_id = request.POST.get('tax_id')
        social_security_id = request.POST.get('social_security_id')
        citizen_card_place_of_issue = request.POST.get('citizen_card_place_of_issue')
        passport_place_of_issue = request.POST.get('passport_place_of_issue')
        citizen_card_date_of_issue = request.POST.get('citizen_card_date_of_issue')
        if citizen_card_date_of_issue:
            citizen_card_date_of_issue2 = datetime.strptime(citizen_card_date_of_issue, "%Y-%m-%d")
            citizen_card_date_of_issue2 = citizen_card_date_of_issue2.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['citizen_card_date_of_issue'] = citizen_card_date_of_issue2

        passport_date_of_issue = request.POST.get('passport_date_of_issue')
        if passport_date_of_issue:
            passport_date_of_issue2 = datetime.strptime(passport_date_of_issue, "%Y-%m-%d")
            passport_date_of_issue2 = passport_date_of_issue2.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['passport_date_of_issue'] = passport_date_of_issue2
        

        #contact details section
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')

        
        #current address section
        current_province = request.POST.get('current_province')
        current_city = request.POST.get('current_city')
        current_district = request.POST.get('current_district')
        current_commune = request.POST.get('current_commune')
        current_address = request.POST.get('current_address')
        current_country = request.POST.get('current_country')
        current_landmark = request.POST.get('current_landmark')
        current_longitude = request.POST.get('current_longitude')
        current_latitude = request.POST.get('current_latitude')

        # permarnent address section
        is_current_address_same_permanent_address = request.POST.get('is-permanent-same-current')
        if is_current_address_same_permanent_address:
            permanent_address = current_address
            permanent_city = current_city
            permanent_district = current_district
            permanent_province = current_province
            permanent_commune = current_commune
            permanent_country = current_country
            permanent_landmark = current_landmark
            permanent_longitude = current_longitude
            permanent_latitude = current_latitude
        else:
            permanent_address = request.POST.get('permanent_address')
            permanent_city = request.POST.get('permanent_city')
            permanent_district = request.POST.get('permanent_district')
            permanent_province = request.POST.get('permanent_province')
            permanent_commune = request.POST.get('permanent_commune')
            permanent_country = request.POST.get('permanent_country')
            permanent_landmark = request.POST.get('permanent_landmark')
            permanent_longitude = request.POST.get('permanent_longitude')
            permanent_latitude = request.POST.get('permanent_latitude')

        
        new_body = {
            "firstname":firstname,
            "lastname":lastname,
            "middle_name":middle_name,
            "place_of_birth":place_of_birth,
            "gender":gender,
            "occupations":occupations,
            "nationality":nationality,
            "beneficiary":beneficiary,
            "unique_reference":unique_reference,
            "citizen_card_id":citizen_card_id,
            "passport_id":passport_id,
            "tax_id":tax_id,
            "social_security_id":social_security_id,
            "citizen_card_place_of_issue":citizen_card_place_of_issue,
            "passport_place_of_issue":passport_place_of_issue,
            #contact detail saction
            "email":email,
            "mobile_number":mobile_number,
            #current address section
            "current_address":current_address,
            "current_province":current_province,
            "current_city":current_city,
            "current_district":current_district,
            "current_commune":current_commune,
            "current_country":current_country,
            "current_landmark":current_landmark,
            "current_longitude":current_longitude,
            "current_latitude":current_latitude,
            #permanent address section
            "permanent_address":permanent_address,
            "permanent_city":permanent_city,
            "permanent_district":permanent_district,
            "permanent_province":permanent_province,
            "permanent_commune":permanent_commune,
            "permanent_country":permanent_country,
            "permanent_landmark":permanent_landmark,
            "permanent_longitude":permanent_longitude,
            "permanent_latitude":permanent_latitude,
            "profile_picture_url": request.POST.get('profile_picture_url')
        }
        body.update(new_body)
        self.logger.info("Params: {} ".format(body))
        

        url = api_settings.ADMIN_UPDATE_CUSTOMER.format(customer_id)
        success, status_code, message, data = RestFulClient.put(
                url = url,
                headers=self._get_headers(),
                loggers=self.logger,
                params=body)

        self.logger.info('========== Finish updating Member Customer ==========')

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated profile successfully'
            )
            data = self.get_member_detail(customer_id=customer_id)
            return render(request, self.template_name, data)
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

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

        body['created_timestamp'] = request.POST.get('created_timestamp')
        body['last_updated_timestamp'] = request.POST.get('last_updated_timestamp')
        body['id'] = customer_id
        body['date_of_birth'] = date_of_birth
        body['citizen_card_date_of_issue'] = citizen_card_date_of_issue
        body['passport_date_of_issue'] = passport_date_of_issue

        context = {
            'customer_info': body,
            'customer_id': customer_id
        }
        return render(request, self.template_name, context)


    def get_member_detail(self, customer_id):
        context = {}
        url = api_settings.MEMBER_CUSTOMER_PATH
        body = {
            'id': customer_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(
                                                    url= url,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=body)
        self.logger.info('Response_content: {}'.format(data))

        if is_success:
            context = {'customer_info': data['customers'][0]}
            is_suspended = context['customer_info'].get('is_suspended')
            context['customer_info']['is_suspended'] = self.status[is_suspended]
            date_of_birth = context['customer_info']['date_of_birth']
            if date_of_birth:
                context['customer_info']['date_of_birth'] = date_of_birth.split('T')[0]

            citizen_card_date_of_issue = context['customer_info']['citizen_card_date_of_issue']
            if citizen_card_date_of_issue:
                context['customer_info']['citizen_card_date_of_issue'] = citizen_card_date_of_issue.split('T')[0]

            passport_date_of_issue = context['customer_info']['passport_date_of_issue']
            if passport_date_of_issue:
                context['customer_info']['passport_date_of_issue'] = passport_date_of_issue.split('T')[0]

            context['customer_id'] = customer_id
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        return context

