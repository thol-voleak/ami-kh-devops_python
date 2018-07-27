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

from customers.views import CustomerAPIService

logger = logging.getLogger(__name__)

class UpdateView(GroupRequiredMixin, TemplateView, GetHeaderMixin, CustomerAPIService):
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

        # Account Basic
        is_testing_account = bool(request.POST.get('is_testing_account'))
        is_system_account = bool(request.POST.get('is_system_account'))
        acquisition_source = request.POST.get('acquisition_source')
        referrer_user_type_id = int(request.POST.get("referrer_user_type")) if request.POST.get(
            "referrer_user_type") else None
        referrer_user_id = int(request.POST.get("referrer_user_id")) if request.POST.get("referrer_user_id") else None
        beneficiary = request.POST.get("beneficiary")

        # Basic Setup
        unique_reference = request.POST.get('unique_reference')
        customer_classification_id = int(request.POST.get("customer_classification_id")) if request.POST.get(
            "customer_classification_id") else None
        mm_card_type_id = int(request.POST.get('mm_card_type_id')) if request.POST.get('mm_card_type_id') else None
        mm_card_level_id = int(request.POST.get('mm_card_level_id')) if request.POST.get('mm_card_level_id') else None
        mm_factory_card_number = request.POST.get('mm_factory_card_number')
        is_require_otp = bool(request.POST.get('is_require_otp'))

        # Personal Details
        tin_number = request.POST.get('tin_number')
        title = request.POST.get('title')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        suffix = request.POST.get('suffix')
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth != '':
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth = date_of_birth.strftime('%Y-%m-%dT%H:%M:%SZ')
        place_of_birth = request.POST.get('place_of_birth')
        gender = request.POST.get('gender')
        ethnicity = request.POST.get('ethnicity')
        nationality = request.POST.get('nationality')
        employer = request.POST.get('employer')
        occupation = request.POST.get('occupation')
        occupation_title = request.POST.get('occupation_title')
        township_code = request.POST.get('township_code')
        township_name = request.POST.get('township_name')
        mother_name = request.POST.get('mother_name')
        mother_maiden_name = request.POST.get('mother_maiden_name')
        civil_status = request.POST.get('civil_status')

        # Contract Details
        email = request.POST.get('email')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        secondary_mobile_number = request.POST.get('secondary_mobile_number')
        tertiary_mobile_number = request.POST.get('tertiary_mobile_number')
        telephone_number = request.POST.get('telephone_number')

        # Address
        # Current Address
        current_address = {
            'citizen_association': request.POST.get('current_address_citizen_association'),
            'neighbourhood_association': request.POST.get('current_address_neighbourhood_association'),
            'address': request.POST.get('current_address_address'),
            'commune': request.POST.get('current_address_commune'),
            'district': request.POST.get('current_address_district'),
            'city': request.POST.get('current_address_city'),
            'province': request.POST.get('current_address_province'),
            'postal_code': request.POST.get('current_address_postal_code'),
            'country': request.POST.get('current_address_country'),
            'landmark': request.POST.get('current_address_landmark'),
            'longitude': request.POST.get('current_address_longitude'),
            'latitude': request.POST.get('current_address_latitude')
        }
        # Permanent Address
        is_permanent_same_current = bool(request.POST.get('is_permanent_same_current'))
        if is_permanent_same_current:
            permanent_address = current_address
        else:
            permanent_address = {
                'citizen_association': request.POST.get('permanent_address_citizen_association'),
                'neighbourhood_association': request.POST.get('permanent_address_neighbourhood_association'),
                'address': request.POST.get('permanent_address_address'),
                'commune': request.POST.get('permanent_address_commune'),
                'district': request.POST.get('permanent_address_district'),
                'city': request.POST.get('permanent_address_city'),
                'province': request.POST.get('permanent_address_province'),
                'postal_code': request.POST.get('permanent_address_postal_code'),
                'country': request.POST.get('permanent_address_country'),
                'landmark': request.POST.get('permanent_address_landmark'),
                'longitude': request.POST.get('permanent_address_longitude'),
                'latitude': request.POST.get('permanent_address_latitude')
            }
        address = {
            'current_address': current_address,
            'permanent_address': permanent_address
        }

        # KYC Details
        # Primary Identity
        primary_issue_date = request.POST.get('primary_identity_issue_date')
        if primary_issue_date != '':
            primary_issue_date = datetime.strptime(primary_issue_date, "%Y-%m-%d")
            primary_issue_date = primary_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        primary_expire_date = request.POST.get('primary_identity_expired_date')
        if primary_expire_date != '':
            primary_expire_date = datetime.strptime(primary_expire_date, "%Y-%m-%d")
            primary_expire_date = primary_expire_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        primary_identity = {
            'type': request.POST.get('primary_identity_type'),
            'identity_id': request.POST.get('primary_identity_id'),
            'status': int(request.POST.get('primary_identity_status')) if request.POST.get(
                "primary_identity_status") else None,
            'place_of_issue': request.POST.get('primary_identity_place_of_issue'),
            'issue_date': primary_issue_date,
            'expired_date': primary_expire_date,
            'front_identity_url': request.POST.get('primary_identity_front_url'),
            'back_identity_url': request.POST.get('primary_identity_back_url'),
            'signature_url': request.POST.get('primary_signature_attachment_url')
        }
        # Secondary Identity
        secondary_issue_date = request.POST.get('secondary_identity_issue_date')
        if secondary_issue_date != '':
            secondary_issue_date = datetime.strptime(secondary_issue_date, "%Y-%m-%d")
            secondary_issue_date = secondary_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        secondary_expire_date = request.POST.get('secondary_identity_expired_date')
        if secondary_expire_date != '':
            secondary_expire_date = datetime.strptime(secondary_expire_date, "%Y-%m-%d")
            secondary_expire_date = secondary_expire_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        secondary_identity = {
            'type': request.POST.get('secondary_identity_type'),
            'identity_id': request.POST.get('secondary_identity_id'),
            'status': int(request.POST.get('secondary_identity_status')) if request.POST.get(
                "secondary_identity_status") else None,
            'place_of_issue': request.POST.get('secondary_identity_place_of_issue'),
            'issue_date': secondary_issue_date,
            'expired_date': secondary_expire_date,
            'front_identity_url': request.POST.get('secondary_identity_front_url'),
            'back_identity_url': request.POST.get('secondary_identity_back_url'),
            'signature_url': request.POST.get('secondary_signature_attachment_url')
        }
        # Tertiary Identity
        tertiary_issue_date = request.POST.get('tertiary_identity_issue_date')
        if tertiary_issue_date != '':
            tertiary_issue_date = datetime.strptime(tertiary_issue_date, "%Y-%m-%d")
            tertiary_issue_date = tertiary_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        tertiary_expire_date = request.POST.get('tertiary_identity_expired_date')
        if tertiary_expire_date != '':
            tertiary_expire_date = datetime.strptime(tertiary_expire_date, "%Y-%m-%d")
            tertiary_expire_date = tertiary_expire_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        tertiary_identity = {
            'type': request.POST.get('tertiary_identity_type'),
            'identity_id': request.POST.get('tertiary_identity_id'),
            'status': int(request.POST.get('tertiary_identity_status')) if request.POST.get(
                "tertiary_identity_status") else None,
            'place_of_issue': request.POST.get('tertiary_identity_place_of_issue'),
            'issue_date': tertiary_issue_date,
            'expired_date': tertiary_expire_date,
            'front_identity_url': request.POST.get('tertiary_identity_front_url'),
            'back_identity_url': request.POST.get('tertiary_identity_back_url'),
            'signature_url': request.POST.get('tertiary_signature_attachment_url')
        }
        verify_date = request.POST.get('kyc_verify_date')
        if verify_date != '':
            verify_date = datetime.strptime(verify_date, "%Y-%m-%d")
            verify_date = verify_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        kyc = {
            'primary_identity': primary_identity,
            'secondary_identity': secondary_identity,
            'tertiary_identity': tertiary_identity,
            'level': int(request.POST.get('kyc_level')) if request.POST.get(
                "kyc_level") else None,
            'remark': request.POST.get('kyc_remark'),
            'verify_by': request.POST.get('kyc_verify_by'),
            'verify_date': verify_date,
            'risk_level': request.POST.get('kyc_risk_level')
        }

        # Profile Additionals
        additional = {
            'profile_picture_url': request.POST.get('additional_profile_picture_url'),
            'tax_id_card_photo_url': request.POST.get('additional_tax_id_card_photo_url'),
            'field_1_name': request.POST.get('additional_field_1_name'),
            'field_2_name': request.POST.get('additional_field_2_name'),
            'field_3_name': request.POST.get('additional_field_3_name'),
            'field_4_name': request.POST.get('additional_field_4_name'),
            'field_5_name': request.POST.get('additional_field_5_name'),
            'field_1_value': request.POST.get('additional_field_1_value'),
            'field_2_value': request.POST.get('additional_field_2_value'),
            'field_3_value': request.POST.get('additional_field_3_value'),
            'field_4_value': request.POST.get('additional_field_4_value'),
            'field_5_value': request.POST.get('additional_field_5_value'),
            'supporting_file_1_url': request.POST.get('additional_supporting_file_1_url'),
            'supporting_file_2_url': request.POST.get('additional_supporting_file_2_url'),
            'supporting_file_3_url': request.POST.get('additional_supporting_file_3_url'),
            'supporting_file_4_url': request.POST.get('additional_supporting_file_4_url'),
            'supporting_file_5_url': request.POST.get('additional_supporting_file_5_url'),
        }

        user_type_list = self._get_user_type_list()
        referrer_user_type = None
        if referrer_user_type_id is not None:
            referrer_user_type_name = [user['name'] for user in user_type_list if user['id'] == referrer_user_type_id][0]
            referrer_user_type = {
                "id": referrer_user_type_id,
                "name": referrer_user_type_name
            }

        new_body = {
            'is_system_account': is_system_account,
            'is_testing_account': is_testing_account,
            'acquisition_source': acquisition_source,
            'referrer_user_type': referrer_user_type,
            'referrer_user_id': referrer_user_id,
            'beneficiary': beneficiary,

            'unique_reference': unique_reference,
            'mm_card_type_id': mm_card_type_id,
            'mm_card_level_id': mm_card_level_id,
            'mm_factory_card_number': mm_factory_card_number,
            'is_require_otp': is_require_otp,
            'customer_classification_id': customer_classification_id,

            'tin_number': tin_number,
            'title': title,
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'suffix': suffix,
            'date_of_birth': date_of_birth,
            'place_of_birth': place_of_birth,
            'gender': gender,
            'ethnicity': ethnicity,
            'nationality': nationality,
            'employer': employer,
            'occupation': occupation,
            'occupation_title': occupation_title,
            'township_code': township_code,
            'township_name': township_name,
            'mother_name': mother_name,
            'mother_maiden_name': mother_maiden_name,
            'civil_status': civil_status,
            'email': email,
            'primary_mobile_number': primary_mobile_number,
            'secondary_mobile_number': secondary_mobile_number,
            'tertiary_mobile_number': tertiary_mobile_number,
            'telephone_number': telephone_number,
            'address': address,
            'kyc': kyc,
            'additional': additional
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
            context = self.get_member_detail(customer_id)
            return render(request, self.template_name, context)
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

        customer_info = self.format_profile_data(body)
        customer_info['id'] = request.POST.get('customer_id')
        customer_info['is_suspended'] = request.POST.get('is_suspended')
        customer_info['active_suspend_reason'] = request.POST.get('suspend_reason')
        customer_info['created_timestamp'] = request.POST.get('created_date')
        customer_info['last_updated_timestamp'] = request.POST.get('last_updated_date')
        customer_info['kyc']['last_updated_timestamp'] = request.POST.get('kyc_updated_date')
        context = {
            'customer_info': customer_info,
            'customer_id': customer_id
        }
        drop_down_context = self.prepare_drop_down_list_context()
        context.update(drop_down_context)

        return render(request, self.template_name, context)

    def get_member_detail(self, customer_id):
        context = {}
        url = api_settings.MEMBER_CUSTOMER_PATH
        body = {
            'id': customer_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(
                                                    url=url,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=body)
        self.logger.info('Response_content: {}'.format(data))

        if is_success:
            data = self.format_profile_data(data['customers'][0])
            is_suspended = data.get('is_suspended')
            data['is_suspended'] = self.status[is_suspended]
            context['customer_info'] = data
            context['customer_id'] = customer_id
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

        drop_down_list_context = self.prepare_drop_down_list_context()
        context.update(drop_down_list_context)

        return context

    def format_profile_data(self, data):
        # Convert date format
        date_of_birth = data['date_of_birth']
        if date_of_birth:
            data['date_of_birth'] = date_of_birth.split('T')[0]

        primary_issue_date = data['kyc']['primary_identity']['issue_date']
        if primary_issue_date:
            data['kyc']['primary_identity']['issue_date'] = primary_issue_date.split('T')[0]
        primary_expiry_date = data['kyc']['primary_identity']['expired_date']
        if primary_expiry_date:
            data['kyc']['primary_identity']['expired_date'] = primary_expiry_date.split('T')[0]

        secondary_issue_date = data['kyc']['secondary_identity']['issue_date']
        if secondary_issue_date:
            data['kyc']['secondary_identity']['issue_date'] = secondary_issue_date.split('T')[0]
        secondary_expiry_date = data['kyc']['secondary_identity']['expired_date']
        if secondary_expiry_date:
            data['kyc']['secondary_identity']['expired_date'] = secondary_expiry_date.split('T')[0]

        tertiary_issue_date = data['kyc']['tertiary_identity']['issue_date']
        if tertiary_issue_date:
            data['kyc']['tertiary_identity']['issue_date'] = tertiary_issue_date.split('T')[0]
        tertiary_expiry_date = data['kyc']['tertiary_identity']['expired_date']
        if tertiary_expiry_date:
            data['kyc']['tertiary_identity']['expired_date'] = tertiary_expiry_date.split('T')[0]

        kyc_verify_date = data['kyc']['verify_date']
        if kyc_verify_date:
            data['kyc']['verify_date'] = kyc_verify_date.split('T')[0]

        return data

    def prepare_drop_down_list_context(self):
        context = {}
        # Get Classification list
        classification_list = self.get_classification(None)
        context['classification_list'] = classification_list

        # Get MM card type list
        mm_card_type_list = self.get_mm_card_type(None)
        context['mm_card_type_list'] = mm_card_type_list

        # Get MM card level list
        mm_card_level_list = self.get_mm_card_level(None)
        context['mm_card_level_list'] = mm_card_level_list

        # Get KYC level list
        kyc_level_list = self.get_kyc_level(None)
        context['kyc_level_list'] = kyc_level_list

        return context

    def _get_user_type_list(self):
        return [{'id': 3, 'name': 'system-user'}, {'id': 2, 'name': 'agent'}, {'id': 1, 'name': 'customer'}]

