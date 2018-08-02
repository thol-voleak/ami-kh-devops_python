from braces.views import GroupRequiredMixin

from agents.views import AgentAPIService

import logging

from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from datetime import datetime
from django.utils import dateparse
from django.http import HttpResponseRedirect
from web_admin.restful_client import RestFulClient
from django.conf import settings
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentUpdate(GroupRequiredMixin, TemplateView, AgentAPIService):
    group_required = "CAN_EDIT_AGENT_DETAILS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agents/update.html"
    get_agent_identity_url = api_settings.GET_AGENT_IDENTITY_URL
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentUpdate, self).dispatch(request, *args, **kwargs)

    def get_mm_card_type_list(self):
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_MM_CARD_TYPES,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params={})
        return data

    def get_mm_card_level_list(self, card_type_id):
        params = {
            "mm_card_type_id": card_type_id
        }
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_MM_CARD_TYPE_LEVELS,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=params)
        return data

    def get_agent_classification_list(self):
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_AGENT_CLASSIFICATION_URL,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params={"paging": False})
        return data.get('classifications', [])

    def get_accreditation_status(self):
        country_code = self.get_country_code()
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_ACCREDITATION_STATUS,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params={"country_code": country_code})
        return data

    def _get_user_type_list(self):
        return [{'id': 3, 'name': 'system-user'}, {'id': 2, 'name': 'agent'}, {'id': 1, 'name': 'customer'}]

    def get_country_code(self):
        url = api_settings.CONFIGURATION_DETAIL_URL.format(scope='global',
                                                           key='country')
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if success:
            return data.get("value")
        else:
            return None

    def get_mm_card_level(request):
        card_type_id = request.POST['card_type_id']
        url = settings.DOMAIN_NAMES + api_settings.GET_MM_CARD_TYPE_LEVELS
        params = {
            "mm_card_type_id": card_type_id
        }
        result = ajax_functions._post_method(request, url, "", logger, params)
        return result

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start showing Update Agent page ==========')
        context = super(AgentUpdate, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        agent_types_list, agent_type_status = self.get_agent_types(agent_id)
        currencies = self.get_currencies(agent_id)[0]
        agent_profile = self.get_agent_profile(agent_id)
        mm_card_types = self.get_mm_card_type_list()
        mm_card_levels = {}
        if agent_profile['mm_card_type_id'] is not None:
            mm_card_levels = self.get_mm_card_level_list(agent_profile['mm_card_type_id'])
        agent_classification_list = self.get_agent_classification_list()
        accreditation_status_list = self.get_accreditation_status()

        if agent_profile['created_timestamp'] is not None:
            created_date = dateparse.parse_datetime(agent_profile['created_timestamp'])
            agent_profile['created_date'] = created_date

        if agent_profile['last_updated_timestamp'] is not None:
            last_updated_timestamp = dateparse.parse_datetime(agent_profile['last_updated_timestamp'])
            agent_profile['last_updated_date'] = last_updated_timestamp

        if agent_profile['bank']['end_date'] is not None:
            bank_end_date = dateparse.parse_datetime(agent_profile['bank']['end_date'])
            agent_profile['bank_end_date'] = bank_end_date

        if agent_profile['bank']['register_date'] is not None:
            bank_register_date = dateparse.parse_datetime(agent_profile['bank']['register_date'])
            agent_profile['bank_register_date'] = bank_register_date

        if agent_profile['contract']['sign_date'] is not None:
            contract_sign_date = dateparse.parse_datetime(agent_profile['contract']['sign_date'])
            agent_profile['contract_sign_date'] = contract_sign_date

        if agent_profile['contract']['issue_date'] is not None:
            contract_issue_date = dateparse.parse_datetime(agent_profile['contract']['issue_date'])
            agent_profile['contract_issue_date'] = contract_issue_date

        if agent_profile['contract']['expired_date'] is not None:
            contract_expired_date = dateparse.parse_datetime(agent_profile['contract']['expired_date'])
            agent_profile['contract_expired_date'] = contract_expired_date

        if agent_profile['date_of_birth'] is not None:
            date_of_birth = dateparse.parse_datetime(agent_profile['date_of_birth'])
            agent_profile['date_of_birth'] = date_of_birth

        if agent_profile['accreditation']['verify_date'] is not None:
            accreditation_verify_date = dateparse.parse_datetime(agent_profile['accreditation']['verify_date'])
            agent_profile['accreditation_verify_date'] = accreditation_verify_date

        if agent_profile['accreditation']['primary_identity']['issue_date'] is not None:
            primary_issue_date = dateparse.parse_datetime(agent_profile['accreditation']['primary_identity']['issue_date'])
            agent_profile['primary_issue_date'] = primary_issue_date

        if agent_profile['accreditation']['primary_identity']['expired_date'] is not None:
            primary_expire_date = dateparse.parse_datetime(agent_profile['accreditation']['primary_identity']['expired_date'])
            agent_profile['primary_expire_date'] = primary_expire_date

        if agent_profile['accreditation']['secondary_identity']['issue_date'] is not None:
            secondary_issue_date = dateparse.parse_datetime(agent_profile['accreditation']['secondary_identity']['issue_date'])
            agent_profile['secondary_issue_date'] = secondary_issue_date

        if agent_profile['accreditation']['primary_identity']['expired_date'] is not None:
            secondary_expire_date = dateparse.parse_datetime(agent_profile['accreditation']['secondary_identity']['expired_date'] )
            agent_profile['secondary_expire_date'] = secondary_expire_date

        agent_identity, status_get_agent_identity = self.get_agent_identity(agent_id)

        context = {
            'agent_types': agent_types_list,
            'currencies': currencies,
            'agent_profile': agent_profile,
            'mm_card_types': mm_card_types,
            'mm_card_levels': mm_card_levels,
            'agent_classification_list': agent_classification_list,
            'accreditation_status_list': accreditation_status_list,
            'msgs': {
                'update_msg_failed': self.request.session.pop('agent_update_msg_failed', None),
            }
        }

        if len(agent_identity['agent_identities']) > 0:
            context.update({'status_get_agent_identity': agent_identity['agent_identities'][0]})

        self.logger.info('========== Finished showing Update Agent page ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating agent ==========')
        agent_id = kwargs['agent_id']
        user_type_list = self._get_user_type_list()

        # Account Basic
        acquisition_source = request.POST.get('acquisition_source')
        referrer_user_type_id = int(request.POST.get("referrer_user_type")) if request.POST.get("referrer_user_type") else None
        referrer_user_id = int(request.POST.get("referrer_user_id")) if request.POST.get("referrer_user_id") else None
        is_testing_account = bool(request.POST.get('is_testing_account'))
        is_system_account = bool(request.POST.get('is_system_account'))

        # Basic Setup
        agent_type_id = int(request.POST.get('agent_type_id'))
        unique_reference = request.POST.get('unique_reference')
        mm_card_type_id = int(request.POST.get('mm_card_types')) if request.POST.get('mm_card_types') else None
        mm_card_level_id = int(request.POST.get('mm_card_levels')) if request.POST.get('mm_card_levels') else None
        mm_factory_card_number = request.POST.get('mm_factory_card_number')
        model_type = request.POST.get('model_type')
        is_require_otp = bool(request.POST.get('is_require_otp'))
        agent_classification_id = int(request.POST.get("agent_classification_id")) if request.POST.get("agent_classification_id") else None

        # Personal Details
        tin_number = request.POST.get('tin_number')
        title = request.POST.get('title')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        middle_name = request.POST.get('middle_name')
        suffix = request.POST.get('suffix')
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth != '':
            date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
            date_of_birth = date_of_birth.strftime('%Y-%m-%dT%H:%M:%SZ')
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
        # local languages fields
        tin_number_local = request.POST.get('tin_number_local')
        title_local = request.POST.get('title_local')
        first_name_local = request.POST.get('first_name_local')
        last_name_local = request.POST.get('last_name_local')
        middle_name_local = request.POST.get('middle_name_local')
        suffix_local = request.POST.get('suffix_local')
        place_of_birth_local = request.POST.get('place_of_birth_local')
        gender_local = request.POST.get('gender_local')
        occupation_local = request.POST.get('occupation_local')
        occupation_title_local = request.POST.get('occupation_title_local')
        township_name_local = request.POST.get('township_name_local')
        national_id_number_local = request.POST.get('national_id_number_local')
        mother_name_local = request.POST.get('mother_name_local')

        # Contract Details
        email = request.POST.get('email')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        secondary_mobile_number = request.POST.get('secondary_mobile_number')
        tertiary_mobile_number = request.POST.get('tertiary_mobile_number')

        # Address
        # Current Address
        current_address = {
            'citizen_association': request.POST.get('current_citizen_association'),
            'neighbourhood_association': request.POST.get('current_neighbourhood_association'),
            'address': request.POST.get('current_address'),
            'commune': request.POST.get('current_commune'),
            'district': request.POST.get('current_district'),
            'city': request.POST.get('current_city'),
            'country': request.POST.get('current_country'),
            'province': request.POST.get('current_province'),
            'postal_code': request.POST.get('current_postal_code'),
            'landmark': request.POST.get('current_landmark'),
            'longitude': request.POST.get('current_longitude'),
            'latitude': request.POST.get('current_latitude'),
            # local languages fields
            'address_local': request.POST.get('current_address_local'),
            'commune_local': request.POST.get('current_commune_local'),
            'district_local': request.POST.get('current_district_local'),
            'city_local': request.POST.get('current_city_local'),
            'country_local': request.POST.get('current_country_local'),
            'province_local': request.POST.get('current_province_local'),
            'postal_code_local': request.POST.get('current_postal_code_local')
        }

        # Permanent Address
        is_permanent_same_current = request.POST.get('is_permanent_same_current')
        if is_permanent_same_current:
            permanent_address = current_address
        else:
            permanent_address = {
                'citizen_association': request.POST.get('permanent_citizen_association'),
                'neighbourhood_association': request.POST.get('permanent_neighbourhood_association'),
                'address': request.POST.get('permanent_address'),
                'commune': request.POST.get('permanent_commune'),
                'district': request.POST.get('permanent_district'),
                'city': request.POST.get('permanent_city'),
                'country': request.POST.get('permanent_country'),
                'province': request.POST.get('permanent_province'),
                'postal_code': request.POST.get('permanent_postal_code'),
                'landmark': request.POST.get('permanent_landmark'),
                'longitude': request.POST.get('permanent_longitude'),
                'latitude': request.POST.get('permanent_latitude'),
                # local languages fields
                'address_local': request.POST.get('permanent_address_local'),
                'commune_local': request.POST.get('permanent_commune_local'),
                'district_local': request.POST.get('permanent_district_local'),
                'city_local': request.POST.get('permanent_city_local'),
                'country_local': request.POST.get('permanent_country_local'),
                'province_local': request.POST.get('permanent_province_local'),
                'postal_code_local': request.POST.get('permanent_postal_code_local')
            }
        address = {
            'current_address': current_address,
            'permanent_address': permanent_address
        }

        # Bank Details
        bank_register_date = request.POST.get('bank_register_date')
        if bank_register_date != '':
            bank_register_date = datetime.strptime(bank_register_date, "%Y-%m-%d")
            bank_register_date = bank_register_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        bank_end_date = request.POST.get('bank_end_date')
        if bank_end_date != '':
            bank_end_date = datetime.strptime(bank_end_date, "%Y-%m-%d")
            bank_end_date = bank_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        bank = {
            'name': request.POST.get('bank_name'),
            'account_status': int(request.POST.get('bank_account_status')) if request.POST.get("bank_account_status") else None,
            'account_name': request.POST.get('bank_account_name'),
            'account_number': request.POST.get('bank_account_number'),
            'branch_area': request.POST.get('bank_branch_area'),
            'branch_city': request.POST.get('bank_branch_city'),
            'register_date': bank_register_date,
            'register_source': request.POST.get('bank_register_source'),
            'is_verified': bool(request.POST.get('bank_verify_status')),
            'end_date': bank_end_date,
            # local language fields
            'name_local': request.POST.get('bank_name_local'),
            'branch_area_local': request.POST.get('bank_branch_area_local'),
            'branch_city_local': request.POST.get('bank_branch_city_local')
        }

        # Contract Details
        contract_sign_date = request.POST.get('contract_sign_date')
        if contract_sign_date != '':
            contract_sign_date = datetime.strptime(contract_sign_date, "%Y-%m-%d")
            contract_sign_date = contract_sign_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        contract_issue_date = request.POST.get('contract_issue_date')
        if contract_issue_date != '':
            contract_issue_date = datetime.strptime(contract_issue_date, "%Y-%m-%d")
            contract_issue_date = contract_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        contract_expiry_date = request.POST.get('contract_expiry_date')
        if contract_expiry_date != '':
            contract_expiry_date = datetime.strptime(contract_expiry_date, "%Y-%m-%d")
            contract_expiry_date = contract_expiry_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        contract = {
            'release': request.POST.get('contract_release'),
            'type': request.POST.get('contract_type'),
            'number': request.POST.get('contract_number'),
            'extension_type': request.POST.get('contract_extension_type'),
            'sign_date': contract_sign_date,
            'issue_date': contract_issue_date,
            'expired_date': contract_expiry_date,
            'notification_alert': request.POST.get('notification_alert'),
            'day_of_period_reconciliation': int(request.POST.get('reconciliation_period_days')) if request.POST.get("reconciliation_period_days") else None,
            'file_url': request.POST.get('contract_file'),
            'assessment_information_url': request.POST.get('assessment_information')
        }

        # Profile Accreditation Details
        # Primary Identity
        primary_issue_date = request.POST.get('primary_issue_date')
        if primary_issue_date != '':
            primary_issue_date = datetime.strptime(primary_issue_date, "%Y-%m-%d")
            primary_issue_date = primary_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        primary_expire_date = request.POST.get('primary_expire_date')
        if primary_expire_date != '':
            primary_expire_date = datetime.strptime(primary_expire_date, "%Y-%m-%d")
            primary_expire_date = primary_expire_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        primary_identity = {
            'type': request.POST.get('primary_identity_type'),
            'identity_id': request.POST.get('primary_identity_id'),
            'status': int(request.POST.get('primary_identity_status')) if request.POST.get("primary_identity_status") else None,
            'place_of_issue': request.POST.get('primary_place_of_issue'),
            'issue_date': primary_issue_date,
            'expired_date': primary_expire_date,
            'front_identity_url': request.POST.get('primary_front_identity_attachment'),
            'back_identity_url': request.POST.get('primary_back_identity_attachment'),
            # local language fields
            'identity_id_local': request.POST.get('primary_identity_id_local')
        }
        # Secondary Section
        secondary_issue_date = request.POST.get('secondary_issue_date')
        if secondary_issue_date != '':
            secondary_issue_date = datetime.strptime(secondary_issue_date, "%Y-%m-%d")
            secondary_issue_date = secondary_issue_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        secondary_expire_date = request.POST.get('secondary_expire_date')
        if secondary_expire_date != '':
            secondary_expire_date = datetime.strptime(secondary_expire_date, "%Y-%m-%d")
            secondary_expire_date = secondary_expire_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        secondary_identity = {
            'type': request.POST.get('secondary_identity_type'),
            'identity_id': request.POST.get('secondary_identity_id'),
            'status': int(request.POST.get('secondary_identity_status')) if request.POST.get("secondary_identity_status") else None,
            'place_of_issue': request.POST.get('secondary_place_of_issue'),
            'issue_date': secondary_issue_date,
            'expired_date': secondary_expire_date,
            'front_identity_url': request.POST.get('secondary_front_identity_attachment'),
            'back_identity_url': request.POST.get('secondary_back_identity_attachment'),
            # local language fields
            'identity_id_local': request.POST.get('secondary_identity_id_local')
        }
        verify_date = request.POST.get('accreditation_verify_date')
        if verify_date != '':
            verify_date = datetime.strptime(verify_date, "%Y-%m-%d")
            verify_date = verify_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        accreditation = {
            'primary_identity': primary_identity,
            'secondary_identity': secondary_identity,
            'status_id': int(request.POST.get('accreditation_status')) if request.POST.get("accreditation_status") else None,
            'remark': request.POST.get('accreditation_remark'),
            'verify_by': request.POST.get('accreditation_verify_by'),
            'verify_date': verify_date,
            'risk_level': request.POST.get('accreditation_risk_level')
        }

        # Profile Additionals
        additional = {
            'acquiring_sale_executive_name': request.POST.get('acquiring_sales_executive_name'),
            'acquiring_sale_executive_id': request.POST.get('acquiring_sales_executive_id'),
            'relationship_manager_name': request.POST.get('relationship_manager_name'),
            'relationship_manager_id': request.POST.get('relationship_manager_id'),
            'sale_region': request.POST.get('sales_region'),
            'commercial_account_manager': request.POST.get('commercial_account_manager'),
            'profile_picture_url': request.POST.get('profile_picture'),
            'national_id_photo_url': request.POST.get('national_id_photo'),
            'tax_id_card_photo_url': request.POST.get('tax_id_card_photo'),
            'field_1_name': request.POST.get('field_1_name'),
            'field_2_name': request.POST.get('field_2_name'),
            'field_3_name': request.POST.get('field_3_name'),
            'field_4_name': request.POST.get('field_4_name'),
            'field_5_name': request.POST.get('field_5_name'),
            'field_1_value': request.POST.get('field_1_value'),
            'field_2_value': request.POST.get('field_2_value'),
            'field_3_value': request.POST.get('field_3_value'),
            'field_4_value': request.POST.get('field_4_value'),
            'field_5_value': request.POST.get('field_5_value'),
            'supporting_file_1_url': request.POST.get('supporting_file_1'),
            'supporting_file_2_url': request.POST.get('supporting_file_2'),
            'supporting_file_3_url': request.POST.get('supporting_file_3'),
            'supporting_file_4_url': request.POST.get('supporting_file_4'),
            'supporting_file_5_url': request.POST.get('supporting_file_5'),
            # local language fields
            'acquiring_sale_executive_name_local': request.POST.get('acquiring_sale_executive_name_local'),
            'relationship_manager_name_local': request.POST.get('relationship_manager_name_local'),
            'sale_region_local': request.POST.get('sale_region_local'),
            'commercial_account_manager_local': request.POST.get('commercial_account_manager_local')
        }

        referrer_user_type = None
        if referrer_user_type_id is not None:
            referrer_user_type_name = [user['name'] for user in user_type_list if user['id'] == referrer_user_type_id][0]
            referrer_user_type = {
                "id": referrer_user_type_id,
                "name": referrer_user_type_name
            }
        data = {
            'acquisition_source': acquisition_source,
            'referrer_user_type': referrer_user_type,
            'referrer_user_id': referrer_user_id,
            'is_system_account': is_system_account,
            'is_testing_account': is_testing_account,

            'agent_type_id': agent_type_id,
            'unique_reference': unique_reference,
            'mm_card_type_id': mm_card_type_id,
            'mm_card_level_id': mm_card_level_id,
            'mm_factory_card_number': mm_factory_card_number,
            'model_type': model_type,
            'is_require_otp': is_require_otp,
            'agent_classification_id': agent_classification_id,

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
            'occupation': occupation,
            'occupation_title': occupation_title,
            'township_code': township_code,
            'township_name': township_name,
            'national_id_number': national_id_number,
            'mother_name': mother_name,
            'email': email,
            'primary_mobile_number': primary_mobile_number,
            'secondary_mobile_number': secondary_mobile_number,
            'tertiary_mobile_number': tertiary_mobile_number,
            # local language fields
            'tin_number_local': tin_number_local,
            'title_local': title_local,
            'first_name_local': first_name_local,
            'last_name_local': last_name_local,
            'middle_name_local': middle_name_local,
            'suffix_local': suffix_local,
            'place_of_birth_local': place_of_birth_local,
            'gender_local': gender_local,
            'occupation_local': occupation_local,
            'occupation_title_local': occupation_title_local,
            'township_name_local': township_name_local,
            'national_id_number_local': national_id_number_local,
            'mother_name_local': mother_name_local,
            'address': address,
            'bank': bank,
            'contract': contract,
            'accreditation': accreditation,
            'additional': additional
        }

        # date_fields = ["date_of_birth", "primary_issue_date", "primary_expire_date", "secondary_issue_date",
        #                "secondary_expire_date"]
        # for key in date_fields:
        #     if not data.get(key, ''):
        #         del data[key]

        # for key, value in data.items():
        #     if not value:
        #         data[key] = ''

        data, success = self._put_method(api_path=api_settings.AGENT_UPDATE_PATH.format(agent_id=agent_id),
                                         func_description="Agent",
                                         logger=logger, params=data)
        self.logger.info('========== Finished updating agent ==========')
        if success:
            request.session['agent_update_msg'] = 'Updated data successfully'
            previous_page = request.POST.get('previous_page')
            if previous_page:
                return HttpResponseRedirect(previous_page)
            return redirect('agents:agent-list')
        else:
            request.session['agent_update_msg_failed'] = data
            return redirect(request.META['HTTP_REFERER'])
