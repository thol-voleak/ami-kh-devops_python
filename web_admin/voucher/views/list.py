from authentications.apps import InvalidAccessToken
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import settings
from web_admin import setup_logger, api_settings
from web_admin.api_settings import SEARCH_SERVICE
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from braces.views import GroupRequiredMixin
from django.contrib import messages
from web_admin.utils import calculate_page_range_from_page_info


logger = logging.getLogger(__name__)


class VoucherList(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "voucher/list.html"
    group_required = "CAN_VIEW_VOUCHER_LIST"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(VoucherList, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start render Vouchers List page==========')
        # status_list = self._get_status_list()
        permissions = {}
        permissions['CAN_CREATE_VOUCHER_ACTION'] = self.check_membership(['CAN_CREATE_VOUCHER_ACTION'])

        permissions['CAN_HOLD_VOUCHER_ACTION'] = self.check_membership(['CAN_HOLD_VOUCHER_ACTION'])
        permissions['CAN_UNHOLD_VOUCHER_ACTION'] = self.check_membership(['CAN_UNHOLD_VOUCHER_ACTION'])

        context = {
            'permissions': permissions,
            # 'claim_status_list': status_list,
            # 'hold_status_list': self._get_hold_status_list(),
            'cash_in_user_type_list': self._get_user_type_cash_in_list(),
            'cash_in_user_type' : '',
            # 'cancel_status_list': self._get_cancel_status_list(),
            'voucher_type_list': self._get_voucher_type_list(),
            # 'distributed_status_list': self._get_distributed_status_list(),
            # 'delete_status_list': self._get_delete_status_list(),
            'voucher_status_list': self._get_voucher_status_list(),
            'voucher_ownership_list': self._get_voucher_ownership_list(),
            'sof_types': self._get_sof_types(),
            'services': self._get_services_list(),
        }
        self.logger.info('========== Finish render Vouchers List page==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        voucher_id = request.POST.get('voucher_id')
        # claim_status = request.POST.get('claim_status')
        cash_in_id = request.POST.get('cash_in_id')
        cash_out_id = request.POST.get('cash_out_id')
        from_date = request.POST.get('create_date_from')
        to_date = request.POST.get('create_date_to')
        expire_from_date = request.POST.get('expiration_date_from')
        expire_to_date = request.POST.get('expiration_date_to')
        # hold_status = request.POST.get('hold_status')
        cash_in_user_type = request.POST.get('user_type_cash_in')

        opening_page_index = request.POST.get('current_page_index')

        cash_in_order_id = request.POST.get('cash_in_order_id')
        cash_out_order_id = request.POST.get('cash_out_order_id')
        issuer_user_id = request.POST.get('issuer_user_id')
        distributed_user_id = request.POST.get('distributed_user_id')
        # cancel_status = request.POST.get('cancel_status')
        voucher_type = request.POST.get('voucher_type')
        # distributed_status = request.POST.get('distributed_status')
        voucher_group = request.POST.get('voucher_group')
        # delete_status = request.POST.get('delete_status')
        voucher_status = request.POST.get('voucher_status')
        voucher_ownership = request.POST.get('voucher_ownership')

        body = {}
        body['page_index'] = int(opening_page_index)
        if cash_in_user_type != '':
            body['cash_in_user_type'] = cash_in_user_type
        if cash_in_id:
            body['cash_in_user_id'] = int(cash_in_id)
        if cash_out_id:
            body['cash_out_user_id'] = int(cash_out_id)
        if voucher_id:
            body['voucher_id'] = voucher_id

        if voucher_status != "All":
            body['is_deleted'] = True if voucher_status == "Deleted" else False
            body['is_cancelled'] = True if voucher_status == "Cancelled" else False
            body['is_on_hold'] = True if voucher_status == "On Hold" else False

        if voucher_ownership != "All":
            body['is_used'] = True if voucher_ownership == 'Claimed' else False
            body['distributed_status'] = True if voucher_ownership == 'Claimed' else False

        # if claim_status == 'True':
        #     body['is_used'] = True
        # if claim_status == 'False':
        #     body['is_used'] = False
        # if hold_status != '':
        #     body['is_on_hold'] = True if hold_status == 'True' else False
        if cash_in_order_id:
            body['cash_in_order_id'] = int(cash_in_order_id)
        if cash_out_order_id:
            body['cash_out_order_id'] = int(cash_out_order_id)
        if issuer_user_id:
            body['issuer_user_id'] = int(issuer_user_id)
        if distributed_user_id:
            body['distributed_user_id'] = int(distributed_user_id)
        # if cancel_status != '':
        #     body['is_cancelled'] = True if cancel_status == 'True' else False

        if from_date:
            new_from_created_timestamp = datetime.strptime(from_date, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp

        if to_date:
            new_to_created_timestamp = datetime.strptime(to_date, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp

        if expire_from_date:
            new_expire_from_timestamp = datetime.strptime(expire_from_date, "%Y-%m-%d")
            new_expire_from_timestamp = new_expire_from_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_expire_date_timestamp'] = new_expire_from_timestamp

        if expire_to_date:
            new_to_expire_timestamp = datetime.strptime(expire_to_date, "%Y-%m-%d")
            new_to_expire_timestamp = new_to_expire_timestamp.replace(hour=23, minute=59, second=59)
            new_to_expire_timestamp = new_to_expire_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_expire_date_timestamp'] = new_to_expire_timestamp

        if voucher_type != '':
            body['voucher_type'] = voucher_type
        # if distributed_status != '':
        #     body['distributed_status'] = True if distributed_status == 'True' else False
        if voucher_group != '':
            body['voucher_group'] = voucher_group
        # if delete_status != '':
        #     body['is_deleted'] = True if delete_status == 'True' else False

        self.logger.info('========== Start searching Vouchers ==========')
        data = self._search_for_vouchers(body)
        self.logger.info('========== Finished searching Vouchers ==========')
        permissions = {}
        permissions['CAN_VIEW_VOUCHER_DETAILS'] = check_permissions_by_user(self.request.user,
                                                                            'CAN_VIEW_VOUCHER_DETAILS')
        permissions['CAN_CREATE_VOUCHER_ACTION'] = check_permissions_by_user(self.request.user,
                                                                            'CAN_CREATE_VOUCHER_ACTION')

        permissions['CAN_HOLD_VOUCHER_ACTION'] = self.check_membership(['CAN_HOLD_VOUCHER_ACTION'])
        permissions['CAN_UNHOLD_VOUCHER_ACTION'] = self.check_membership(['CAN_UNHOLD_VOUCHER_ACTION'])
        page = data['page']
        context = {
            'data': data['vouchers'],
            'paginator': page,
			'search_count': page['total_elements'],
			'page_range': calculate_page_range_from_page_info(page),
            'voucher_id': voucher_id,
            # 'claim_status_list': self._get_status_list(),
            # 'selected_status': claim_status,
            'voucher_status': voucher_status,
            'voucher_ownership': voucher_ownership,
            'voucher_status_list': self._get_voucher_status_list(),
            'voucher_ownership_list': self._get_voucher_ownership_list(),
            'cash_in_id': cash_in_id,
            'cash_out_id': cash_out_id,
            'create_date_from': from_date,
            'create_date_to': to_date,
            'expiration_date_from': expire_from_date,
            'expiration_date_to': expire_to_date,
            'permissions': permissions,
            # 'hold_status_list': self._get_hold_status_list(),
            # 'hold_status': hold_status,
            'cash_in_user_type_list': self._get_user_type_cash_in_list(),
            'cash_in_user_type' : cash_in_user_type,
            # 'cancel_status_list': self._get_cancel_status_list(),
            'cash_out_order_id': cash_out_order_id,
            'cash_in_order_id': cash_in_order_id,
            'issuer_user_id': issuer_user_id,
            'distributed_user_id': distributed_user_id,
            # 'cancel_status': cancel_status,
            'voucher_type_list': self._get_voucher_type_list(),
            'voucher_type': voucher_type,
            # 'distributed_status_list': self._get_distributed_status_list(),
            # 'distributed_status': distributed_status,
            'voucher_group': voucher_group,
            # 'delete_status_list': self._get_delete_status_list(),
            # 'delete_status': delete_status,
            'services': self._get_services_list(),
            'sof_types': self._get_sof_types()
        }
        return render(request, self.template_name, context)


    # def _get_status_list(self):
    #     return [
    #         {"name": "All", "value": ""},
    #         {"name": "Used", "value": "True"},
    #         {"name": "Unused", "value": "False"},
    #     ]

    # def _get_hold_status_list(self):
    #     return [
    #         {"name": "All", "value": ""},
    #         {"name": "Hold", "value": "True"},
    #         {"name": "Unhold", "value": "False"},
    #     ]

    def _get_user_type_cash_in_list(self):
        return [
            {"name": "All", "value": ""},
            {"name": "Agent", "value": "agent"},
            {"name": "Customer", "value": "customer"},
        ]

    # def _get_cancel_status_list(self):
    #     return [
    #         {"name": "All", "value": ""},
    #         {"name": "Yes", "value": "True"},
    #         {"name": "No", "value": "False"},
    #     ]
    def _search_for_vouchers(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.SEARCH_VOUCHERS,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data

    @staticmethod
    def _get_voucher_type_list():
        return [
            {"name": "All", "value": ""},
            {"name": "REMITTANCE", "value": "REMITTANCE"},
            {"name": "3rd Party Vouchers", "value": "3rd Party Vouchers"}
        ]

    # @staticmethod
    # def _get_distributed_status_list():
    #     return [
    #         {"name": "All", "value": ""},
    #         {"name": "Yes", "value": "True"},
    #         {"name": "No", "value": "False"}
    #     ]

    # @staticmethod
    # def _get_delete_status_list():
    #     return [
    #         {"name": "All", "value": ""},
    #         {"name": "Deleted", "value": "True"},
    #         {"name": "None", "value": "False"}
    #     ]

    @staticmethod
    def _get_voucher_status_list():
        return ["All", "Created", "On Hold", "Cancelled", "Deleted"]\

    @staticmethod
    def _get_voucher_ownership_list():
        return ["All", "None", "Distributed", "Claimed"]

    def _get_sof_types(self):
        success, status_code, data  = RestFulClient.get(url=api_settings.SOF_TYPES_URL, loggers=self.logger, headers=self._get_headers())
        return data

    def _get_services_list(self):
        self.logger.info('========== Start Getting services list ==========')
        url = api_settings.SEARCH_SERVICE
        success, status_code, status_message, data = RestFulClient.post(url=url, headers=self._get_headers(),
                                                          loggers=self.logger,
                                                           params={"paging":False},
                                                           timeout=settings.GLOBAL_TIMEOUT)
        if success:
            self.logger.info("Response_content_count:{}".format(len(data)))
            data = data.get("services",None)
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        self.logger.info('========== Finish Get services list ==========')
        self.logger.info(data)

        return data

