from braces.views import GroupRequiredMixin
from django.contrib import messages
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, RestFulClient
from web_admin.api_settings import BALANCE_ADJUSTMENT_PATH, SERVICE_LIST_URL
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken
from web_admin.api_logger import API_Logger



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
        context['data'] = data
        context['search_count'] = 0
        context['status_list'] = self.status_list
        context['status_id'] = ''

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        count = 0

        order_id = request.POST.get('order_id')
        service_id = request.POST.get('service_name')
        payer_user_id = request.POST.get('payer_user_id')
        payer_user_type_id = request.POST.get('payer_user_type_id')
        payee_user_id = request.POST.get('payee_user_id')
        payee_user_type_id = request.POST.get('payee_user_type_id')
        ref_order_id = request.POST.get('ref_order_id')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        service_list = self.get_services_list()

        status_id = request.POST.get('status_id')
        requested_by_id = request.POST.get('requested_by_id')
        approved_by_id = request.POST.get('approved_by_id')
        payer_sof_type_id = request.POST.get('payer_sof_type_id')
        payee_sof_type_id = request.POST.get('payee_sof_type_id')


        body = {}
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
        if ref_order_id:
            body['reference_order_id'] = ref_order_id
        if status_id:
            body['status'] = status_id
        if requested_by_id:
            body['created_user_id'] = requested_by_id
        if approved_by_id:
            body['approved_user_id'] = approved_by_id
        

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
        self.logger.info('========== Finished searching Balance Adjustment ==========')
        if is_success:
            count = len(data)
            self.logger.info("Response_content_count:{}".format(count))

            context = {'order_list': data,
                   'order_id': order_id,
                   'service_id': service_id,
                   'data': service_list,
                   'payer_user_id': payer_user_id,
                   'payer_user_type_id':payer_user_type_id,
                   'payee_user_id': payee_user_id,
                   'payee_user_type_id':payee_user_type_id,
                   'search_count': count,
                   'requested_by_id': requested_by_id,
                   'approved_by_id': approved_by_id,
                   'payer_sof_type_id': payer_sof_type_id,
                   'payee_sof_type_id': payee_sof_type_id,
                   'status_list': self.status_list,
                   'date_from': from_created_timestamp,
                   'date_to': to_created_timestamp,
                   'ref_order_id': ref_order_id
                   }
            if status_id:
                context['status_id'] = int(status_id)
            return render(request, self.template_name, context)
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        elif status_message == 'timeout':
            messages.add_message(request, messages.ERROR, 'Request timed-out, please try again or contact system administrator')
            return redirect('balance_adjustment:balance_adjustment_list')

    # def refine_data(self, data):
    #     for item in data:
    #         item['status'] = STATUS_ORDER.get(item['status'])
    #     return data


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
        
        
        