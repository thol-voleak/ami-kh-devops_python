from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
import logging
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from django.shortcuts import render
from django.shortcuts import redirect
logger = logging.getLogger(__name__)


class EditView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "password_center/edit.html"
    logger = logger

    group_required = "CAN_MANAGE_PASSWORD_CENTER"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info("========== Start getting password center update identity type ==========")
        identity_type_id = int(kwargs.get('identityTypeId'))
        rule_data = self.get_rule_config(identity_type_id)
        identity_type_data = self.get_identity_ype(identity_type_id)
        result = {'rule_data': rule_data, 'identity_type_id': identity_type_id,'identity_type_data':identity_type_data}
        self.logger.info("========== Finish getting password center updage identity type ==========")
        return result

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start updating password rule config ==========")
        identity_type_id = request.POST.get('identity_type_id')
        if request.POST.get('password_type_name') == "Alphanumeric":
            params = {
                'min_length': request.POST.get('rule_config_min_length'),
                'max_length': request.POST.get('rule_config_max_length'),
                'expire_after': request.POST.get('rule_config_expire_after'),
                'disallow_last_password': request.POST.get('rule_config_disallow_last_password'),
                'min_numeric_characters': request.POST.get('rule_config_min_numeric_characters'),
                'min_alpha_numeric_characters': request.POST.get('rule_config_min_alpha_numeric_characters'),
                'min_alphabet_characters': request.POST.get('rule_config_min_alphabet_characters'),
                'min_distinct_characters': request.POST.get('rule_config_min_distinct_characters'),
                'min_special_characters': request.POST.get('rule_config_min_special_characters'),
                'min_uppercase_characters': request.POST.get('rule_config_min_uppercase_characters'),
                'min_lowercase_characters': request.POST.get('rule_config_min_lowercase_characters'),
                'not_allowed_characters': request.POST.get('rule_config_not_allowed_characters')
            }
        else:
            params = {
                'min_length': request.POST.get('rule_config_min_length'),
                'max_length': request.POST.get('rule_config_max_length'),
                'expire_after': request.POST.get('rule_config_expire_after'),
                'disallow_last_password': request.POST.get('rule_config_disallow_last_password'),
                'max_repeated_numeric_characters': request.POST.get('rule_config_max_repeated_numeric_characters')
            }

        self.logger.info(params)
        url = api_settings.UPDATE_PASSWORD_CENTER_RULE_CONFIG_URL.format(identity_type_id=identity_type_id)

        success, status_code, status_message, data = RestFulClient.post(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)
        self.logger.info("========== Finish updating password rule config ==========")
        if success:
            request.session['password_center_update_msg'] = 'Saved data successfully'
            return redirect('password_center:list')
        else:
            rule_data = self.get_rule_config(identity_type_id)
            identity_type_data = self.get_identity_ype(identity_type_id)
            context = {'error_msg': status_message, 'rule_data':rule_data, 'identity_type_data':identity_type_data, 'identity_type_id': identity_type_id}
            return render(request, 'password_center/edit.html', context)

    def get_identity_ype(self, identity_type_id):
        url = api_settings.PASSWORD_CENTER_IDENTITY_TYPE_URL
        body = {
            'id': identity_type_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=body)
        data = data or {}
        return data

    def get_rule_config(self, identity_type_id):
        url = api_settings.PASSWORD_CENTER_RULE_CONFIG_URL
        body = {
            'identity_type_id': identity_type_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(
            url=url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=body)
        data = data or {}
        return data
