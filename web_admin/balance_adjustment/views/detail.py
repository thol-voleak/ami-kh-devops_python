from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import render
from authentications.apps import InvalidAccessToken
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin
import logging


logger = logging.getLogger(__name__)


class BalanceAdjustmentDetailView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "balance_adjustment/detail.html"
    logger=logger

    group_required = "SYS_BAL_ADJUST_HISTORY"
    button_permission = "SYS_BAL_ADJUST_APPROVE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))

        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BalanceAdjustmentDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start getting balance adjustment detail ==========')
        context = super(BalanceAdjustmentDetailView, self).get_context_data(**kwargs)
        reference_id = context['ReferenceId']
        body = {'reference_id':reference_id}
        url = api_settings.BALANCE_ADJUSTMENT_PATH
        #url = 'http://localhost:43931/additional_detail' # status: REJECT_FAIL
        #url = 'http://localhost:43932/additional_detail'  # status: APPROVE_FAIL
        #url = 'http://localhost:43933/additional_detail'  # status: Created
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        permissions = {}
        permissions['SYS_BAL_ADJUST_APPROVE'] = check_permissions_by_user(self.request.user, 'SYS_BAL_ADJUST_APPROVE')

        balanceAdjustmentRespone = data['balance_adjustment_reference'][0]
        referenceServiceGroupInfo = self._get_service_group_detail(balanceAdjustmentRespone['reference_service_group_id'])
        referenceServiceInfo = self._get_service_detail(balanceAdjustmentRespone['reference_service_id'])

        context = {'order': data['balance_adjustment_reference'][0],
                   'referenceServiceGroupInfo': referenceServiceGroupInfo,
                   'referenceServiceInfo': referenceServiceInfo,
                   'show_buttons': True,
                   'permissions': permissions}
        self.logger.info('========== Finish getting balance adjustment detail ==========')
        return context

    def post(self, request, *args, **kwargs):
        context = super(BalanceAdjustmentDetailView, self).get_context_data(**kwargs)
        button = request.POST.get('submit')
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, self.button_permission))
        if button == 'Approve':
            return self._do_approval(request)
        elif button == 'Reject':
            return self._do_reject(request)

    def _do_approval(self, request):
        self.logger.info('========== Start Approve balance adjustment order ==========')
        reference_id = request.POST.get('reference_id')
        url = api_settings.APPROVE_BAL_ADJUST_PATH.format(reference_id=reference_id)
        #url = 'http://localhost:4393/general_error_approval'

        body = {'reason': request.POST.get('reason_for_approval_or_reject')}


        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish Approve balance adjustment order ==========')
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Payment is approved successfully'
            )
            return redirect('balance_adjustment:balance_adjustment_list')
        elif status_code.lower() in ["general_error"]:
            error_msg = 'Other error, please contact system administrator'
            return self._handle_error(error_msg, reference_id)
            # If get error timeout, response as success to client
        elif status_code.lower() in ["external_call_timeout", "internal_call_timeout","sof_timeout", "timeout"]:
            self.logger.info('get timeout error from server but considers as success to client')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Payment is approved successfully'
            )
            return redirect('balance_adjustment:balance_adjustment_list')
        elif status_message == 'timeout':
            messages.add_message(
                request,
                messages.ERROR,
                'Request timed-out, please try again or contact system administrator'
            )
            return redirect('balance_adjustment:balance_adjustment_detail', ReferenceId=reference_id)
        else:
            return self._handle_error(status_message, reference_id)


    def _do_reject(self, request):
        self.logger.info('========== Start Reject balance adjustment order ==========')
        reference_id = request.POST.get('reference_id')
        url = api_settings.APPROVE_BAL_ADJUST_PATH.format(reference_id=reference_id)
        #url = 'http://localhost:43938/general_error_reject'
        body = {'reason': request.POST.get('reason_for_approval_or_reject')}

        is_success, status_code, status_message = RestFulClient.delete(url=url,
                                                                       headers=self._get_headers(),
                                                                       loggers=self.logger,
                                                                       params=body)
        API_Logger.delete_logging(loggers=self.logger, params=body, response={}, status_code=status_code)

        self.logger.info('========== Finish Reject balance adjustment order ==========')
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Payment is rejected successfully'
            )
            return redirect('balance_adjustment:balance_adjustment_list')
        elif status_code.lower() in ["general_error"]:
            error_msg = 'Other error, please contact system administrator'
            return self._handle_error(error_msg, reference_id)
        elif status_message == 'timeout':
            messages.add_message(
                request,
                messages.ERROR,
                'Request timed-out, please try again or contact system administrator'
            )
            return redirect('balance_adjustment:balance_adjustment_detail', ReferenceId=reference_id)
        else:
            return self._handle_error(status_message, reference_id)

    def _handle_error(self, message, reference_id):
        messages.add_message(
            self.request,
            messages.ERROR,
            message
        )
        return redirect(self.request.META['HTTP_REFERER'])

    def _get_service_group_detail(self, service_group_id):
        if service_group_id == None:
            return None
        url = api_settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)
        self.logger.info('========== start getting service group detail ==========')
        is_success, status_code, data = RestFulClient.get(url=url,
                                                          headers=self._get_headers(),
                                                          loggers=self.logger)
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                                status_code=status_code)
        context = None
        if is_success:
            context = data
        self.logger.info('========== Finished getting service group detail ==========')
        return context

    def _get_service_detail(self, service_id):
        if service_id == None:
            return None
        url = api_settings.SERVICE_DETAIL_URL.format(service_id)
        self.logger.info('========== start getting service detail ==========')
        is_success, status_code, data = RestFulClient.get(url=url,
                                                          headers=self._get_headers(),
                                                          loggers=self.logger)
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        context = None
        if is_success:
            context = data
        self.logger.info('========== Finished getting service detail ==========')
        return context
