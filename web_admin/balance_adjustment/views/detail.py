from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic.base import TemplateView

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
        order_id = context['OrderId']
        body = {'order_id':order_id}
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.BALANCE_ADJUSTMENT_PATH,
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

        context = {'order': data[0],
                   'permissions': permissions}
        self.logger.info('========== Finish getting balance adjustment detail ==========')
        return context

    def post(self, request, *args, **kwargs):
        context = super(BalanceAdjustmentDetailView, self).get_context_data(**kwargs)
        order_id = context['OrderId']
        reference_id = request.POST.get('reference_id')
        url = api_settings.APPROVE_BAL_ADJUST_PATH.format(reference_id=reference_id)
        body = {'reason': request.POST.get('reason_for_approval_or_reject')}

        button = request.POST.get('submit')
        if button == 'Approve':
            self.logger.info('========== Start Approve balance adjustment order ==========')
            is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

            API_Logger.post_logging(loggers=self.logger, params={}, response=data,
                                   status_code=status_code)
            self.logger.info('========== Finish Approve balance adjustment order ==========')
            if is_success:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Payment is approved successfully'
                )
                return redirect('balance_adjustment:balance_adjustment_list')
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    status_message
                )
                return redirect('balance_adjustment:balance_adjustment_detail', OrderId=order_id)
        elif button == 'Reject':
            self.logger.info('========== Start Reject balance adjustment order ==========')
            is_success, status_code, status_message = RestFulClient.delete(url=url,
                                                                               headers=self._get_headers(),
                                                                               loggers=self.logger,
                                                                               params=body)
            API_Logger.delete_logging(loggers=self.logger, params={}, response={},status_code=status_code)

            self.logger.info('========== Finish Reject balance adjustment order ==========')
            if is_success:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Payment is rejected successfully'
                )
                return redirect('balance_adjustment:balance_adjustment_list')
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    status_message
                )
                return redirect('balance_adjustment:balance_adjustment_detail', OrderId=order_id)


