'''
History:
- 2017-05-03: Initialize empty Class with template HTML name (Steve Le)
- 2017-05-04: Add logic for Agent registration (Gate Nguyen)
-- API 1: POST api-gateway/agent/v1/agents/{agent_id}/profiles                      [METHOD = _create_agent_profile]
-- API 2: POST api-gateway/agent/v1/agents/{agent_id}/identities                    [METHOD = _create_agent_identity]
-- API 3: POST api-gateway/agent/v1/agents/{agent_id}/sofs/{sof_type}/{currency}    [METHOD = _create_agent_balance]
- 2017-05-05: Corrected API Logic make Agent registration work well (Steve Le)
-- Added logging format and more.
'''

import logging

from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from datetime import datetime
from django.shortcuts import redirect, render
from web_admin.mixins import GetChoicesMixin
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import encrypt_text_agent, setup_logger
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import ajax_functions
from django.conf import settings

from web_admin.api_logger import API_Logger

logger = logging.getLogger(__name__)
logging.captureWarnings(True)




class AgentTypeAndCurrenciesAndIdentityTypeDropDownList(TemplateView, RESTfulMethods):
    def _get_agent_types_list(self):
        data, success = self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                         func_description="Agent Type List",
                                         logger=logger)
        newdata = [i for i in data if not i['is_deleted']]
        return newdata

    def _get_currencies_dropdown(self):
        data, success = self._get_method(api_path=api_settings.GET_ALL_CURRENCY_URL,
                                         func_description="Agent All Currency List",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            try:
                value = data['value']
                currencies = value.split(',')
                result = [currency.split("|")[0] for currency in currencies]
            except:
                result = []
        else:
            result = []
        return result

    def _get_identity_type_list(self):
        api_path = api_settings.GET_IDENTITY_TYPES
        body = {
            "is_deleted": False
        }
        success, status_code, status_message, data = RestFulClient.post(url=api_path,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body)
        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body,
                                response=data.get('identity_types', []),
                                status_code=status_code, is_getting_list=True)
        return data.get('identity_types', [])

    def _get_user_type_list(self):
        return [{'id': 3, 'name': 'system-user'}, {'id': 2, 'name': 'agent'}, {'id': 1, 'name': 'customer'}]

    def _get_mm_card_type_list(self):
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_MM_CARD_TYPES,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params={})
        return data

    def _get_agent_classification_list(self):
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_AGENT_CLASSIFICATION_URL,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params={"paging": False})
        return data.get('classifications', [])

    def _get_country_code(self):
        url = api_settings.CONFIGURATION_DETAIL_URL.format(scope='global',
                                                           key='country')
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if success:
            return data.get("value")
        else:
            return None

    def _get_accreditation_status(self):
        country_code = self._get_country_code()
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_ACCREDITATION_STATUS,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params={"country_code": country_code})
        return data

def get_mm_card_level(request):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_PERFORM_AGENT_REGISTRATION'))
    if not check_permissions_by_user(request.user, 'CAN_PERFORM_AGENT_REGISTRATION'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start get mm card level by card type ==========')
    card_type_id = request.POST['card_type_id']
    url = settings.DOMAIN_NAMES + api_settings.GET_MM_CARD_TYPE_LEVELS
    params = {
        "mm_card_type_id": card_type_id
    }
    result = ajax_functions._post_method(request, url, "", logger, params)
    logger.info('========== Finish get mm card level by card type ==========')
    return result

class AgentRegistration(GroupRequiredMixin, AgentTypeAndCurrenciesAndIdentityTypeDropDownList, GetHeaderMixin):
    group_required = "CAN_PERFORM_AGENT_REGISTRATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agents/registration.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentRegistration, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *arg, **kwargs):
        self.logger.info('========== Start showing Create Agent page ==========')
        # Get API that inherits from parent Class
        currencies = self._get_currencies_dropdown()
        agent_types_list = self._get_agent_types_list()
        identity_type_list = self._get_identity_type_list()
        user_type_list = self._get_user_type_list()
        mm_card_type_list = self._get_mm_card_type_list()
        agent_classification_list = self._get_agent_classification_list()
        agent_accreditation_status_list = self._get_accreditation_status()

        result = {
            'permanent_address_check':True,
            'currencies': currencies,
            'agent_types_list': agent_types_list,
            'identity_type_list': identity_type_list,
            'user_type_list': user_type_list,
            'mm_card_type_list' : mm_card_type_list,
            'agent_classification_list': agent_classification_list,
            'agent_accreditation_status_list': agent_accreditation_status_list,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }
        self.logger.info('========== Finished showing Create Agent page ==========')
        return result

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating agent ==========')

        status = 1  # request.POST.get('status') #TODO: hard fix
        agent_types_list = self._get_agent_types_list()
        currencies = self._get_currencies_dropdown()
        identity_type_list = self._get_identity_type_list()
        user_type_list = self._get_user_type_list()
        mm_card_type_list = self._get_mm_card_type_list()
        agent_classification_list = self._get_agent_classification_list()
        agent_accreditation_status_list = self._get_accreditation_status()
        check_or_not = True
        date_exist_on_context = {}

        # Current Address Section
        current_address_citizen_association = request.POST.get('current_address_citizen_association')
        current_address_neighbourhood_association = request.POST.get('current_address_neighbourhood_association')
        current_address_address = request.POST.get('current_address_address')
        current_address_commune = request.POST.get('current_address_commune')
        current_address_district = request.POST.get('current_address_district')
        current_address_city = request.POST.get('current_address_city')
        current_address_province = request.POST.get('current_address_province')
        current_address_postal_code = request.POST.get('current_address_postal_code')
        current_address_country = request.POST.get('current_address_country')
        current_address_landmark = request.POST.get('current_address_landmark')
        current_address_longitude = request.POST.get('current_address_longitude')
        current_address_latitude = request.POST.get('current_address_latitude')

        # Permanent Address Section
        is_current_address_same_permanent_address = request.POST.get('is-permanent-same-current')
        if is_current_address_same_permanent_address:
            permanent_address_citizen_association = current_address_citizen_association
            permanent_address_neighbourhood_association = current_address_neighbourhood_association
            permanent_address_address = current_address_address
            permanent_address_commune = current_address_commune
            permanent_address_district = current_address_district
            permanent_address_city = current_address_city
            permanent_address_province = current_address_province
            permanent_address_postal_code = current_address_postal_code
            permanent_address_country = current_address_country
            permanent_address_landmark = current_address_landmark
            permanent_address_longitude = current_address_longitude
            permanent_address_latitude = current_address_latitude
        else:
            permanent_address_citizen_association = request.POST.get('permanent_address_citizen_association')
            permanent_address_neighbourhood_association = request.POST.get('permanent_address_neighbourhood_association')
            permanent_address_address = request.POST.get('permanent_address_address')
            permanent_address_commune = request.POST.get('permanent_address_commune')
            permanent_address_district = request.POST.get('permanent_address_district')
            permanent_address_city = request.POST.get('permanent_address_city')
            permanent_address_province = request.POST.get('permanent_address_province')
            permanent_address_postal_code = request.POST.get('permanent_address_postal_code')
            permanent_address_country = request.POST.get('permanent_address_country')
            permanent_address_landmark = request.POST.get('permanent_address_landmark')
            permanent_address_longitude = request.POST.get('permanent_address_longitude')
            permanent_address_latitude = request.POST.get('permanent_address_latitude')
            check_or_not = False

        address = {
            "current_address": {
                "citizen_association": current_address_citizen_association,
                "neighbourhood_association": current_address_neighbourhood_association,
                "address": current_address_address,
                "commune": current_address_commune,
                "district": current_address_district,
                "city": current_address_city,
                "province": current_address_province,
                "postal_code": current_address_postal_code,
                "country": current_address_country,
                "landmark": current_address_landmark,
                "longitude": current_address_longitude,
                "latitude": current_address_latitude
            },
            "permanent_address": {
                "citizen_association": permanent_address_citizen_association,
                "neighbourhood_association": permanent_address_neighbourhood_association,
                "address": permanent_address_address,
                "commune": permanent_address_commune,
                "district": permanent_address_district,
                "city": permanent_address_city,
                "province": permanent_address_province,
                "postal_code": permanent_address_postal_code,
                "country": permanent_address_country,
                "landmark": permanent_address_landmark,
                "longitude": permanent_address_longitude,
                "latitude": permanent_address_latitude
            }
        }

        # Bank Details Section
        bank_name = request.POST.get('bank_name')
        bank_account_status = int(request.POST.get('bank_account_status')) if request.POST.get("bank_account_status") else None
        bank_account_name = request.POST.get('bank_account_name')
        bank_account_number = request.POST.get('bank_account_number')
        bank_branch_area = request.POST.get('bank_branch_area')
        bank_branch_city = request.POST.get('bank_branch_city')
        bank_register_date = request.POST.get('bank_register_date')
        if bank_register_date != '':
            new_bank_register_date = datetime.strptime(bank_register_date, "%Y-%m-%d")
            bank_register_date = new_bank_register_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['bank_register_date'] = new_bank_register_date
        bank_register_source = request.POST.get('bank_register_source')
        bank_is_verified = bool(request.POST.get('bank_is_verified'))
        bank_end_date = request.POST.get('bank_end_date')
        if bank_end_date != '':
            new_bank_end_date = datetime.strptime(bank_end_date, "%Y-%m-%d")
            bank_end_date = new_bank_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['bank_end_date'] = new_bank_end_date

        bank = {
            "name": bank_name,
            "account_status": bank_account_status,
            "account_name": bank_account_name,
            "account_number": bank_account_number,
            "branch_area": bank_branch_area,
            "branch_city": bank_branch_city,
            "register_date": bank_register_date,
            "register_source": bank_register_source,
            "is_verified": bank_is_verified,
            "end_date": bank_end_date
        }

        # Contract Details Section
        contract_release = request.POST.get('contract_release')
        contract_type = request.POST.get('contract_type')
        contract_number = request.POST.get('contract_number')
        contract_extension_type = request.POST.get('contract_extension_type')
        contract_sign_date = request.POST.get('contract_sign_date')
        if contract_sign_date != '':
            new_contract_sign_date = datetime.strptime(contract_sign_date, "%Y-%m-%d")
            contract_sign_date = new_contract_sign_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['contract_sign_date'] = new_contract_sign_date
        contract_issue_date = request.POST.get('contract_issue_date')
        if contract_issue_date != '':
            new_contract_issue_date = datetime.strptime(contract_issue_date, "%Y-%m-%d")
            contract_issue_date = new_contract_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['contract_issue_date'] = new_contract_issue_date
        contract_expired_date = request.POST.get('contract_expired_date')
        if contract_expired_date != '':
            new_contract_expired_date = datetime.strptime(contract_expired_date, "%Y-%m-%d")
            contract_expired_date = new_contract_expired_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['contract_expired_date'] = new_contract_expired_date
        contract_notification_alert = request.POST.get('contract_notification_alert')
        contract_day_of_period_reconciliation = int(request.POST.get('contract_day_of_period_reconciliation')) if request.POST.get("contract_day_of_period_reconciliation") else None
        contract_file_url = request.POST.get('contract_file_url')
        contract_assessment_information_url = request.POST.get('contract_assessment_information_url')

        contract = {
            "type": contract_type,
            "number": contract_number,
            "extension_type": contract_extension_type,
            "sign_date": contract_sign_date,
            "issue_date": contract_issue_date,
            "expired_date": contract_expired_date,
            "notification_alert": contract_notification_alert,
            "day_of_period_reconciliation": contract_day_of_period_reconciliation,
            "release": contract_release,
            "file_url": contract_file_url,
            "assessment_information_url": contract_assessment_information_url
        }

        # Profile Accreditation Section
        # Primary Identity Section
        primary_identity_type = request.POST.get('primary_identity_type')
        primary_identity_status = int(request.POST.get('primary_identity_status')) if request.POST.get("primary_identity_status") else None
        primary_identity_id = request.POST.get('primary_identity_id')
        primary_identity_place_of_issue = request.POST.get('primary_identity_place_of_issue')
        primary_identity_issue_date = request.POST.get('primary_identity_issue_date')
        if primary_identity_issue_date != '':
            new_primary_identity_issue_date = datetime.strptime(primary_identity_issue_date, "%Y-%m-%d")
            primary_identity_issue_date = new_primary_identity_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['primary_identity_issue_date'] = new_primary_identity_issue_date

        primary_identity_expired_date = request.POST.get('primary_identity_expired_date')
        if primary_identity_expired_date != '':
            new_primary_identity_expired_date = datetime.strptime(primary_identity_expired_date, "%Y-%m-%d")
            primary_identity_expired_date = new_primary_identity_expired_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['primary_identity_expired_date'] = new_primary_identity_expired_date
        primary_identity_front_url = request.POST.get('primary_identity_front_url')
        primary_identity_back_url = request.POST.get('primary_identity_back_url')

        # Secondary Identity Section
        secondary_identity_type = request.POST.get('secondary_identity_type')
        secondary_identity_status = int(request.POST.get('secondary_identity_status')) if request.POST.get("secondary_identity_status") else None
        secondary_identity_id = request.POST.get('secondary_identity_id')
        secondary_identity_place_of_issue = request.POST.get('secondary_identity_place_of_issue')
        secondary_identity_issue_date = request.POST.get('secondary_identity_issue_date')
        if secondary_identity_issue_date != '':
            new_secondary_identity_issue_date = datetime.strptime(secondary_identity_issue_date, "%Y-%m-%d")
            secondary_identity_issue_date = new_secondary_identity_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['secondary_identity_issue_date'] = new_secondary_identity_issue_date

        secondary_identity_expired_date = request.POST.get('secondary_identity_expired_date')
        if secondary_identity_expired_date != '':
            new_secondary_identity_expired_date = datetime.strptime(secondary_identity_expired_date, "%Y-%m-%d")
            secondary_identity_expired_date = new_secondary_identity_expired_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['secondary_identity_expired_date'] = new_secondary_identity_expired_date
        secondary_identity_front_url = request.POST.get('secondary_identity_front_url')
        secondary_identity_back_url = request.POST.get('secondary_identity_back_url')

        accreditation_status_id = int(request.POST.get('accreditation_status_id')) if request.POST.get("accreditation_status_id") else None
        accreditation_verify_by = request.POST.get('accreditation_verify_by')
        # accreditation_verify_date = request.POST.get('accreditation_verify_date')
        # if accreditation_verify_date != '':
        #     new_accreditation_verify_date = datetime.strptime(accreditation_verify_date, "%Y-%m-%d")
        #     accreditation_verify_date = new_accreditation_verify_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        #     date_exist_on_context['accreditation_verify_date'] = new_accreditation_verify_date
        accreditation_remark = request.POST.get('accreditation_remark')
        accreditation_risk_level = request.POST.get('accreditation_risk_level')

        accreditation = {
            "primary_identity": {
                "type": primary_identity_type,
                "status": primary_identity_status,
                "identity_id": primary_identity_id,
                "place_of_issue": primary_identity_place_of_issue,
                "issue_date": primary_identity_issue_date,
                "expired_date": primary_identity_expired_date,
                "front_identity_url": primary_identity_front_url,
                "back_identity_url": primary_identity_back_url
            },
            "secondary_identity": {
                "type": secondary_identity_type,
                "status": secondary_identity_status,
                "identity_id": secondary_identity_id,
                "place_of_issue": secondary_identity_place_of_issue,
                "issue_date": secondary_identity_issue_date,
                "expired_date": secondary_identity_expired_date,
                "front_identity_url": secondary_identity_front_url,
                "back_identity_url": secondary_identity_back_url
            },
            "status_id": accreditation_status_id,
            "remark": accreditation_remark,
            "verify_by": accreditation_verify_by,
            # "verify_date": accreditation_verify_date,
            "risk_level": accreditation_risk_level
        }

        # Additionals Section
        additional_acquiring_sale_executive_name = request.POST.get('additional_acquiring_sale_executive_name')
        additional_acquiring_sale_executive_id = request.POST.get('additional_acquiring_sale_executive_id')
        additional_relationship_manager_name = request.POST.get('additional_relationship_manager_name')
        additional_relationship_manager_id = request.POST.get('additional_relationship_manager_id')
        additional_sale_region = request.POST.get('additional_sale_region')
        additional_commercial_account_manager = request.POST.get('additional_commercial_account_manager')
        additional_profile_picture_url = request.POST.get('additional_profile_picture_url')
        additional_national_id_photo_url = request.POST.get('additional_national_id_photo_url')
        additional_tax_id_card_photo_url = request.POST.get('additional_tax_id_card_photo_url')
        additional_field_1_name = request.POST.get('additional_field_1_name')
        additional_field_1_value = request.POST.get('additional_field_1_value')
        additional_field_2_name = request.POST.get('additional_field_2_name')
        additional_field_2_value = request.POST.get('additional_field_2_value')
        additional_field_3_name = request.POST.get('additional_field_3_name')
        additional_field_3_value = request.POST.get('additional_field_3_value')
        additional_field_4_name = request.POST.get('additional_field_4_name')
        additional_field_4_value = request.POST.get('additional_field_4_value')
        additional_field_5_name = request.POST.get('additional_field_5_name')
        additional_field_5_value = request.POST.get('additional_field_5_value')
        additional_supporting_file_1_url = request.POST.get('additional_supporting_file_1_url')
        additional_supporting_file_2_url = request.POST.get('additional_supporting_file_2_url')
        additional_supporting_file_3_url = request.POST.get('additional_supporting_file_3_url')
        additional_supporting_file_4_url = request.POST.get('additional_supporting_file_4_url')
        additional_supporting_file_5_url = request.POST.get('additional_supporting_file_5_url')

        additional = {
            "acquiring_sale_executive_id": additional_acquiring_sale_executive_name,
            "acquiring_sale_executive_name": additional_acquiring_sale_executive_id,
            "relationship_manager_id": additional_relationship_manager_name,
            "relationship_manager_name": additional_relationship_manager_id,
            "sale_region": additional_sale_region,
            "commercial_account_manager": additional_commercial_account_manager,
            "profile_picture_url": additional_profile_picture_url,
            "national_id_photo_url": additional_national_id_photo_url,
            "tax_id_card_photo_url": additional_tax_id_card_photo_url,
            "field_1_name": additional_field_1_name,
            "field_1_value": additional_field_1_value,
            "field_2_name": additional_field_2_name,
            "field_2_value": additional_field_2_value,
            "field_3_name": additional_field_3_name,
            "field_3_value": additional_field_3_value,
            "field_4_name": additional_field_4_name,
            "field_4_value": additional_field_4_value,
            "field_5_name": additional_field_5_name,
            "field_5_value": additional_field_5_value,
            "supporting_file_1_url": additional_supporting_file_1_url,
            "supporting_file_2_url": additional_supporting_file_2_url,
            "supporting_file_3_url": additional_supporting_file_3_url,
            "supporting_file_4_url": additional_supporting_file_4_url,
            "supporting_file_5_url": additional_supporting_file_5_url
        }

        # Account Basics Section
        is_testing_account = bool(request.POST.get("is_testing_account"))
        is_system_account = bool(request.POST.get("is_system_account"))
        acquisition_source = request.POST.get("acquisition_source")
        referrer_user_type_id = int(request.POST.get("referrer_user_type_id")) if request.POST.get("referrer_user_type_id") else None
        referrer_user_id = int(request.POST.get("referrer_user_id")) if request.POST.get("referrer_user_id") else None
        agent_type_id = int(request.POST.get('agent_type_id'))
        identity_type_id = int(request.POST.get('identity_type_id'))
        username = request.POST.get('username')
        password = ''
        auto_generate_password = 'false'
        system_password = request.POST.get('system_password')
        if system_password:
            auto_generate_password = 'true'
        else:
            password = encrypt_text_agent(request.POST.get('password'))
        currency = request.POST.get('currency')
        unique_reference = request.POST.get('unique_reference')
        mm_card_type_id = int(request.POST.get('mm_card_type_id')) if request.POST.get('mm_card_type_id') else None
        mm_card_level_id = int(request.POST.get('mm_card_level_id')) if request.POST.get('mm_card_level_id') else None
        mm_factory_card_number = request.POST.get('mm_factory_card_number')
        model_type = request.POST.get('model_type')
        is_require_otp = bool(request.POST.get('is_require_otp'))
        agent_classification_id = int(request.POST.get('agent_classification_id')) if request.POST.get('agent_classification_id') else None

        # Personal Details Section
        tin_number = request.POST.get('tin_number')
        title = request.POST.get('title')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        suffix = request.POST.get('suffix')
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth != '':
            new_date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth = new_date_of_birth.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_exist_on_context['date_of_birth'] = new_date_of_birth
        place_of_birth = request.POST.get('place_of_birth')
        gender = request.POST.get('gender')
        ethnicity = request.POST.get('ethnicity')
        nationality = request.POST.get('nationality')
        occupation = request.POST.get('occupation')
        occupation_title = request.POST.get('occupation_title')
        township_code = request.POST.get('township_code')
        township_name = request.POST.get('township_name')
        national_id_number = request.POST.get('national_id_number')
        mother_name = request.POST.get('mother_name')

        # Contact Details Section
        email = request.POST.get('email')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        secondary_mobile_number = request.POST.get('secondary_mobile_number')
        tertiary_mobile_number = request.POST.get('tertiary_mobile_number')

        referrer_user_type = None
        if referrer_user_type_id is not None:
            referrer_user_type_name = [user['name'] for user in user_type_list if user['id'] == referrer_user_type_id][0]
            referrer_user_type = {
                "id": referrer_user_type_id,
                "name": referrer_user_type_name
            }

        profile = {
            "is_testing_account": is_testing_account,
            "is_system_account": is_system_account,
            "acquisition_source": acquisition_source,
            "referrer_user_type": referrer_user_type,
            "referrer_user_id": referrer_user_id,
            "agent_type_id": agent_type_id,
            "unique_reference": unique_reference,
            "mm_card_type_id": mm_card_type_id,
            "mm_card_level_id": mm_card_level_id,
            "mm_factory_card_number": mm_factory_card_number,
            "model_type": model_type,
            "is_require_otp": is_require_otp,
            "agent_classification_id": agent_classification_id,
            "tin_number": tin_number,
            "title": title,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "suffix": suffix,
            "date_of_birth": date_of_birth,
            "place_of_birth": place_of_birth,
            "gender": gender,
            "ethnicity": ethnicity,
            "nationality": nationality,
            "occupation": occupation,
            "occupation_title": occupation_title,
            "township_code": township_code,
            "township_name": township_name,
            "national_id_number": national_id_number,
            "mother_name": mother_name,
            "email": email,
            "primary_mobile_number": primary_mobile_number,
            "secondary_mobile_number": secondary_mobile_number,
            "tertiary_mobile_number": tertiary_mobile_number,
            "address": address,
            "bank": bank,
            "contract": contract,
            "accreditation": accreditation,
            "additional": additional
        }

        identity = {
            'identity_type_id': identity_type_id,
            'username': username,
            'password': password,
            'auto_generate_password': auto_generate_password
        }

        body = {
            'profile': profile,
            'identity': identity
        }
        is_success, status_code, status_message, agent_profile_reponse = RestFulClient.post(
                                                    url= api_settings.AGENT_REGISTRATION_URL,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=body)
        identity = {'username': username,
                    'identity_type_id': identity_type_id}
        body = {
            'profile': profile,
            'identity': identity
        }
        self.logger.info("Params: {} ".format(body))
        context = {
            'permanent_address_check':check_or_not,
            'agent_types_list': agent_types_list,
            'context_date':date_exist_on_context,
            'currencies': currencies,
            'identity_type_list': identity_type_list,
            'user_type_list': user_type_list,
            'mm_card_type_list': mm_card_type_list,
            'agent_classification_list': agent_classification_list,
            'agent_accreditation_status_list': agent_accreditation_status_list,
            'agent_profile': profile,
            'identity': identity,
            'context_currency':currency,
            'msgs': {
                'get_msg': status_message,
            }
        }
        agent_id = ''
        if is_success:
            agent_id = agent_profile_reponse['id']
            agent_balance, success = self._create_agent_balance(request, agent_id)
            self.logger.info('========== Finished creating agent ==========')
            if success:
                request.session['agent_registration_msg'] = 'Added agent successfully'
                return redirect('agents:agent_detail', agent_id=agent_id)
            elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            else:
                return render(request, self.template_name, context)
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        else:
            self.logger.info('========== Finished creating agent ==========')
            return render(request, self.template_name, context)


    def _create_agent_balance(self, request, agent_id):

        currency = request.POST.get('currency')
        # sof_type = "cash"  # TODO: Hard code for Sof_Type
        body = {'currency': currency,
                'user_id': agent_id,
                'user_type_id': 2}  #TODO: Hard code for agent_type
        api_path = api_settings.CREATE_AGENT_BALANCE_URL

        is_success, status_code, status_message, data = RestFulClient.post(
                                                    url= api_path,
                                                    headers=self._get_headers(),
                                                    loggers=self.logger,
                                                    params=body)
        return data, is_success