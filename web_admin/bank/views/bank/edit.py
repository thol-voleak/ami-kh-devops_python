from authentications.utils import get_correlation_id_from_username, check_permissions_by_user, get_auth_header
from bank.views.banks_client import BanksClient
from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_logger import API_Logger
from django.conf import settings
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
from braces.views import GroupRequiredMixin

import logging

logger = logging.getLogger(__name__)


class EditView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "SYS_EDIT_BANK"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "bank/edit.html"
    update_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/sof-bank/" + api_settings.API_VERSION + "/admin/banks/{id}"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(EditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get bank detail ==========')
        context = super(EditView, self).get_context_data(**kwargs)
        bank_id = context['bank_id']

        params = {
            'id': bank_id
        }

        is_success, status_code, status_message, bank_detail = BanksClient.get_bank_details(
            params=params, headers=self._get_headers(), logger=self.logger
        )
        API_Logger.post_logging(loggers=self.logger, params=params, response=bank_detail, status_code=status_code)

        self.logger.info('========== Finished get bank detail ==========')

        self.logger.info('========== Start get currency list ==========')

        is_success_currencies, status_code_currencies, currencies = BanksClient.get_currencies_list(
            header=self._get_headers(), logger=self.logger
        )
        API_Logger.get_logging(loggers=self.logger, response=currencies, status_code=status_code_currencies)

        if not is_success:
            messages.error(self.request, status_message)

        if not is_success_currencies:
            messages.error(self.request, currencies)
            currencies = []

        context = {'bank': bank_detail, 'currencies': currencies}
        self.logger.info('========== Finished get currency list ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update bank profile ==========')
        bank_id = kwargs['bank_id']

        name = request.POST.get('name')
        bank_bin = request.POST.get('bin')
        is_active = request.POST.get('is_active')
        description = request.POST.get('description')
        pre_sof_url = request.POST.get('pre_sof_url', '')
        presof_order_read_timeout = request.POST.get('presof_order_read_timeout', '')
        if presof_order_read_timeout:
            presof_order_read_timeout = int(presof_order_read_timeout)
        credit_url = request.POST.get('credit_url')
        debit_url = request.POST.get('debit_url')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        currency = request.POST.get('currency')
        check_status_url = request.POST.get('check_status_url')
        cancel_url = request.POST.get('cancel_url')
        connection_timeout = request.POST.get('connection_timeout')
        read_timeout = request.POST.get('read_timeout')

        if is_active == '1':
            is_active = True
        else:
            is_active = False

        params = {
            "name": name,
            "bin": bank_bin,
            "description": description,
            "pre_sof_url": pre_sof_url,
            "pre_sof_read_timeout": presof_order_read_timeout,
            "is_active": bool(is_active),
            "debit_url": debit_url,
            "credit_url": credit_url,
            "bank_account_number": account_number,
            "bank_account_name": account_name,
            "currency": currency,
            "check_status_url": check_status_url,
            "cancel_url": cancel_url,
            "connection_timeout": connection_timeout,
            "read_timeout": read_timeout
        }

        data, success = self._put_method(api_path=self.update_bank_sof_detail_url.format(id=bank_id),
                                         func_description="Bank Profile",
                                         logger=logger, params=params)
        # API_Logger.put_logging(loggers=self.logger, params=params, response=data)

        if success:
            self.logger.info('========== Finished update bank profile ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Update bank successfully'
            )
            return redirect('bank:bank_sofs_list')
        else:
            if data == 'timeout':
                messages.error(request, "Timeout updating configuration, please try again or contact technical support")
            else:
                messages.error(request, data)
            params['id'] = bank_id

            is_success, status_code, data = BanksClient.get_currencies_list(
                header=self._get_headers(), logger=self.logger
            )

            if not is_success:
                messages.error(request, data)
                data = []

            context = {'bank': params, 'currencies': data}
            self.logger.info('========== Finished update bank profile ==========')
            return render(request, self.template_name, context)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
