from braces.views import GroupRequiredMixin
from django.contrib import messages
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, RestFulClient
from web_admin.api_settings import BALANCE_ADJUSTMENT_PATH, SERVICE_LIST_URL, SERVICE_GROUP_LIST_URL
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken
from web_admin.api_logger import API_Logger
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.utils import check_permissions
import json
from web_admin import api_settings
from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
import logging
from datetime import datetime
logger = logging.getLogger(__name__)



class BalanceAdjustmentListView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "balance_adjustment/list.html"
    logger = logger

    group_required = "SYS_BAL_ADJUST_HISTORY"
    login_url = 'web:permission_denied'
    raise_exception = False

    status_list = [
            {"id": 1, "name": "CREATING"},
            {"id": 2, "name": "CREATE_FAIL"},
            {"id": 3, "name": "CREATED"},
            {"id": 4, "name": "APPROVING"},
            {"id": 5, "name": "APPROVE_FAIL"},
            {"id": 6, "name": "APPROVED"},
            {"id": 7, "name": "REJECTING"},
            {"id": 8, "name": "REJECT_FAIL"},
            {"id": 9, "name": "REJECTED"},
            {"id": 10, "name": "TIMEOUT"},
            {"id": -9999, "name": "IN_PROGRESS"},
    ]

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BalanceAdjustmentListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(BalanceAdjustmentListView, self).get_context_data(**kwargs)
        data = self.get_services_list()
        service_group_list = self.get_service_group_list()
        currency_list = self._get_preload_currencies_dropdown()

        context['data'] = data
        context['service_group_list'] = service_group_list
        context['search_count'] = 0
        context['status_list'] = self.status_list
        context['status_id'] = ''
        context['currencies'] = currency_list
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        count = 0

        order_id = request.POST.get('order_id')
        opening_page_index = request.POST.get('current_page_index')
        service_id = request.POST.get('service_name')
        payer_user_id = request.POST.get('payer_user_id')
        payer_user_type_id = request.POST.get('payer_user_type_id')
        payee_user_id = request.POST.get('payee_user_id')
        payee_user_type_id = request.POST.get('payee_user_type_id')
        ref_order_id = request.POST.get('ref_order_id')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        service_list = self.get_services_list()
        service_group_list = self.get_service_group_list()

        status_id = request.POST.get('status_id')
        requested_by_id = request.POST.get('requested_by_id')
        approved_by_id = request.POST.get('approved_by_id')
        payer_sof_type_id = request.POST.get('payer_sof_type_id')
        payee_sof_type_id = request.POST.get('payee_sof_type_id')
        reference_service_group_id = request.POST.get('reference_service_group_id')
        reference_service_id = request.POST.get('reference_service_id')
        batch_code = request.POST.get('batch_code')
        currency_code = request.POST.get('currency_code')
        currency_list = self._get_preload_currencies_dropdown()

        body = {}
        body['page_index'] = int(opening_page_index)
        if order_id:
            body['order_id'] = order_id
        if service_id:
            body['product_service_id'] = service_id
            service_id = int(service_id)
        if payer_user_id:
            body['payer_user_id'] = payer_user_id
        if payer_user_type_id.isdigit() and payer_user_type_id != '0':
            body['payer_user_type_id'] = int(payer_user_type_id)
        if payee_user_id:
            body['payee_user_id'] = payee_user_id
        if payee_user_type_id.isdigit() and payee_user_type_id != '0':
            body['payee_user_type_id'] = int(payee_user_type_id)
        if payer_sof_type_id.isdigit() and payer_sof_type_id != '0':
            body['payer_user_sof_type_id'] = int(payer_sof_type_id)
        if payee_sof_type_id.isdigit() and payee_sof_type_id != '0':
            body['payee_user_sof_type_id'] = int(payee_sof_type_id)
        if reference_service_group_id.isdigit() and reference_service_group_id != '0':
            reference_service_group_id = int(reference_service_group_id)
            body['reference_service_group_id'] = reference_service_group_id
        if reference_service_id.isdigit() and reference_service_id != '0':
            reference_service_id = int(reference_service_id)
            body['reference_service_id'] = reference_service_id
        if ref_order_id:
            body['reference_order_id'] = ref_order_id
        if status_id:
            body['status'] = status_id
        if requested_by_id:
            body['created_user_id'] = requested_by_id
        if approved_by_id:
            body['approved_user_id'] = approved_by_id
        if batch_code:
            body['batch_code'] = batch_code
        if currency_code:
            body['currency'] = currency_code

        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['created_timestamp_from'] = new_from_created_timestamp

        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['created_timestamp_to'] = new_to_created_timestamp
        
        self.logger.info('========== Start searching balance adjustment ==========')
        self.logger.info("Params: {} ".format(body))

        is_success, status_code, status_message, data = RestFulClient.post(
            url=BALANCE_ADJUSTMENT_PATH,
            headers=self._get_headers(),
            loggers=self.logger,
            params=body
        )
        if is_success:
            balance_adjustment_reference = data['balance_adjustment_reference']
            page = data['page']
            count = len(balance_adjustment_reference)
            self.logger.info("Response_content_count:{}".format(count))
            self.logger.info("Page:{}".format(page))

            context = {'order_list': balance_adjustment_reference,
                       'order_id': order_id,
                       'service_id': service_id,
                       'data': service_list,
                       'service_group_list': service_group_list,
                       'payer_user_id': payer_user_id,
                       'payer_user_type_id': payer_user_type_id,
                       'payee_user_id': payee_user_id,
                       'payee_user_type_id': payee_user_type_id,
                       'search_count': count,
                       'requested_by_id': requested_by_id,
                       'approved_by_id': approved_by_id,
                       'payer_sof_type_id': payer_sof_type_id,
                       'payee_sof_type_id': payee_sof_type_id,
                       'reference_service_group_id': reference_service_group_id,
                       'reference_service_id': reference_service_id,
                       'status_list': self.status_list,
                       'date_from': from_created_timestamp,
                       'date_to': to_created_timestamp,
                       'ref_order_id': ref_order_id,
                       'batch_code': batch_code,
                       'paginator': page,
                       'page_range': calculate_page_range_from_page_info(page),
                       'search_count': page['total_elements'],
                       'currency_code': currency_code,
                       'currencies': currency_list
                       }
            if status_id:
                context['status_id'] = int(status_id)
            self.logger.info('========== Finished searching Balance Adjustment ==========')
            return render(request, self.template_name, context)
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        elif status_message == 'timeout':
            messages.add_message(request, messages.ERROR, 'Request timed-out, please try again or contact system administrator')
            return redirect('balance_adjustment:balance_adjustment_list')

    def get_services_list(self):
        self.logger.info('========== Start Getting services list ==========')
        url = SERVICE_LIST_URL
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(),
                                                            loggers=self.logger)
        if is_success:
            self.logger.info("Response_content_count:{}".format(len(data)))

        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        self.logger.info('========== Finish Get services list ==========')

        return data

    def get_service_group_list(self):
        url = SERVICE_GROUP_LIST_URL
        is_success, status_code, data = RestFulClient.get(url, headers=self._get_headers(), loggers=self.logger)

        if is_success:
            if data is None or data == "":
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        return data

    def _get_preload_currencies_dropdown(self):
        url = api_settings.GET_ALL_PRELOAD_CURRENCY_URL
        is_success, status_code, data = RestFulClient.get(url,
                                                          loggers=self.logger,
                                                          headers=self._get_headers())

        if is_success:
            return data
        else:
            # return empty list data
            return []


class BalanceAdjustmentListActionView(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "SYS_BAL_ADJUST_APPROVE")
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BalanceAdjustmentListActionView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        actionType = data.get("actionType")
        if actionType == 'Approve':
            return self._approve_balance_adjustment_list(data)
        elif actionType == 'Reject':
            return self._reject_balance_adjustment_list(data)

    def _approve_balance_adjustment_list(self, data):
        self.logger.info('========== Start Approve balance adjustment list==========')
        url = api_settings.ORDER_BAL_ADJUST_PATH
        referenceIds = json.loads(data.get("referenceIds"))
        data = {
            "reference_ids": referenceIds,
            "reason": data.get("reason")
        }

        is_success, status_code, status_message, data = RestFulClient.put(
            url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=data
        )

        if is_success:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                str(len(referenceIds)) + " adjustments being Approved. Please wait a while and check again later"
            )

            return JsonResponse({
                "is_success": is_success
            })

        else:
            return JsonResponse({
                "is_success": is_success,
                "status_code": status_code,
                "status_message": status_message,
                "data": data
            })

    def _reject_balance_adjustment_list(self, data):
        self.logger.info('========== Start reject balance adjustment list==========')
        url = api_settings.ORDER_BAL_ADJUST_PATH
        referenceIds = json.loads(data.get("referenceIds"))
        data = {
            "reference_ids": referenceIds,
            "reason": data.get("reason")
        }

        is_success, status_code, status_message, data = RestFulClient.delete_return_data(
            url,
            headers=self._get_headers(),
            loggers=self.logger,
            params=data
        )

        if is_success:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                str(len(referenceIds)) + " adjustments being Rejected. Please wait a while and check again later"
            )

            return JsonResponse({
                "is_success": is_success
            })

        else:
            return JsonResponse({
                "is_success": is_success,
                "status_code": status_code,
                "status_message": status_message,
                "data": data
            })
