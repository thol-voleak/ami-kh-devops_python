from datetime import datetime
from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import RestFulClient
from web_admin import api_settings
from web_admin import settings
from web_admin import setup_logger
from django.shortcuts import render
from django.views.generic.base import TemplateView

from web_admin.api_logger import API_Logger
from web_admin.api_settings import SOF_TYPES_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import CASH_SOFS_URL
from django.contrib import messages

import logging

from web_admin.global_constants import UserType, ORDER_STATUS, ORDER_DETAIL_STATUS, SOF_TYPE, SOFType
from web_admin.utils import calculate_page_range_from_page_info, make_download_file, export_file

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class TransactionHistoryView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_AGENT_INDIVIDUAL_WALLET"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/transaction_history.html'
    logger = logger
    dateUIFormat = "%Y-%m-%d"
    paymentScopeName = 'payment'
    walletViewTransactionHistoryInDaysKey = 'wallet_view_transaction_history_in_days'


    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(TransactionHistoryView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start getting agent transaction history ==========')
        context = super(TransactionHistoryView, self).get_context_data(**kwargs)
        user_id = context['agent_id']
        choices = self._get_choices_types()
        user_type = UserType.AGENT.value
        cash_sof_list = self._get_cash_sof_list(user_id, user_type).get('cash_sofs', [])
        order_detail_status_list = self._get_order_detail_status_list()
        sof_id = request.GET.get('sof_id')
        sof_type_id = request.GET.get('sof_type_id')
        order_detail_status = int(request.GET.get('order_detail_status')) if request.GET.get('order_detail_status') else ''
        opening_page_index = request.GET.get('current_page_index')
        from_created_timestamp = request.GET.get('from_created_timestamp')
        to_created_timestamp = request.GET.get('to_created_timestamp')

        context = {}
        if sof_id is None and sof_type_id is None and opening_page_index is None and from_created_timestamp is None and to_created_timestamp is None:
            body = {}
            body['paging'] = True
            body['page_index'] = 1

            request.session['agent_redirect_from_wallet_view'] = True
            request.session['page_from'] = 'agent'
            request.session['agent_id'] = user_id

            # Set first load default time for Context
            from_created_timestamp = datetime.now()
            to_created_timestamp = datetime.now()
            from_created_timestamp = from_created_timestamp.replace(hour=0, minute=0, second=1)
            to_created_timestamp = to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_from_created_timestamp = from_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            body['from_created_timestamp'] = new_from_created_timestamp
            new_from_created_timestamp = from_created_timestamp.strftime("%Y-%m-%d")
            context['from_created_timestamp'] = new_from_created_timestamp

            body['to_created_timestamp'] = new_to_created_timestamp
            new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%d")
            context['to_created_timestamp'] = new_to_created_timestamp

            body['sof_type_id'] = SOFType.CASH.value
            body['user_type_id'] = UserType.AGENT.value
            body['user_id'] = user_id

            order_balance_movements, page, summaries, success = self._get_transaction_history(body)
            if success:
                if order_balance_movements is not None:
                    result_data = self.format_data(order_balance_movements)
                    has_permission_view_payment_order_detail = check_permissions_by_user(self.request.user,
                                                                                         'CAN_VIEW_PAYMENT_ORDER_DETAIL')
                    for i in order_balance_movements:
                        i['has_permission_view_payment_order_detail'] = has_permission_view_payment_order_detail
                else:
                    result_data = order_balance_movements
                self.logger.info("Page: {}".format(page))
                context.update(
                    {'search_count': page.get('total_elements', 0),
                     'list': result_data,
                     'summaries': summaries,
                     'choices': choices,
                     'cash_sof_list': cash_sof_list,
                     'order_detail_status_list': order_detail_status_list,
                     'paginator': page,
                     'page_range': calculate_page_range_from_page_info(page),
                     'agent_id': user_id,
                     'is_show_export': check_permissions_by_user(self.request.user, "CAN_EXPORT_AGENT_INDIVIDUAL_WALLET")
                     }
                )
            else:
                context.update(
                    {'search_count': 0,
                     'data': [],
                     'paginator': {},
                     'agent_id': user_id,
                     'is_show_export': False
                     }
                )
        else:
            user_type = UserType.AGENT.value
            cash_sof_list = self._get_cash_sof_list(user_id, user_type).get('cash_sofs', [])
            choices = self._get_choices_types()

            body = {}
            body['paging'] = True
            body['page_index'] = int(opening_page_index)
            if sof_id is not '' and sof_id is not None:
                sof_id = int(sof_id)
                body['sof_id'] = sof_id
            if sof_type_id is not '' and sof_type_id is not None:
                body['sof_type_id'] = int(sof_type_id)
            if order_detail_status is not '' and order_detail_status is not None:
                body['status_id_list'] = [int(order_detail_status)]

            body['user_type_id'] = UserType.AGENT.value
            body['user_id'] = user_id


            # validate required search date criteria
            if from_created_timestamp is '' or to_created_timestamp is '':
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Please specify the to and from date search criteria'
                )

                context.update(
                    {'search_count': 0,
                     'list': [],
                     'summaries': [],
                     'choices': choices,
                     'sof_type_id': sof_type_id,
                     'sof_id': sof_id,
                     'order_detail_status': order_detail_status,
                     'cash_sof_list': cash_sof_list,
                     'order_detail_status_list': order_detail_status_list,
                     'paginator': {},
                     'agent_id': user_id,
                     'from_created_timestamp': from_created_timestamp,
                     'to_created_timestamp': to_created_timestamp
                     }
                )
                return render(request, self.template_name, context)
            diffDay = self._getDiffDaysFromUIDateValue(from_created_timestamp, to_created_timestamp)

            # validate fromDate less than or equals to toDate
            if diffDay < 0:
                messages.add_message(
                    request,
                    messages.ERROR,
                    'The from date should be before or equal to the to date'
                )

                context.update(
                    {'search_count': 0,
                     'list': [],
                     'summaries': [],
                     'choices': choices,
                     'sof_type_id': sof_type_id,
                     'sof_id': sof_id,
                     'order_detail_status': order_detail_status,
                     'order_detail_status_list': order_detail_status_list,
                     'cash_sof_list': cash_sof_list,
                     'paginator': {},
                     'agent_id': user_id,
                     'from_created_timestamp': from_created_timestamp,
                     'to_created_timestamp': to_created_timestamp
                     }
                )

                return render(request, self.template_name, context)

            # validate date range
            walletViewInDay = self._getWalletViewInDay()
            if diffDay > int(walletViewInDay):
                messages.add_message(
                    request,
                    messages.ERROR,
                    'Time range over ' + walletViewInDay + ' day(s) is not allowed'
                )

                context.update(
                    {'search_count': 0,
                     'list': [],
                     'summaries': [],
                     'choices': choices,
                     'sof_type_id': sof_type_id,
                     'sof_id': sof_id,
                     'order_detail_status': order_detail_status,
                     'order_detail_status_list': order_detail_status_list,
                     'cash_sof_list': cash_sof_list,
                     'paginator': {},
                     'agent_id': user_id,
                     'from_created_timestamp': from_created_timestamp,
                     'to_created_timestamp': to_created_timestamp
                     }
                )

                return render(request, self.template_name, context)
            # build date range critera for service
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, self.dateUIFormat)
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp

            new_to_created_timestamp = datetime.strptime(to_created_timestamp, self.dateUIFormat)
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp

            if ('download' in request.GET):
                self.logger.info('Exporting agent transaction history')
                file_type = request.GET.get('export_type')
                body['file_type'] = file_type
                body['row_number'] = 5000
                is_success, order_balance_movements = export_file(self, body=body, url_download = api_settings.BALANCE_MOVEMENT_LIST_PATH, api_logger = API_Logger)
                if is_success:
                    response = make_download_file(order_balance_movements, file_type)
                    self.logger.info('Export agent transaction history success')
                    return response
            else:
                self.logger.info('Searching customer transaction history')
                order_balance_movements, page, summaries, success = self._get_transaction_history(body)
                if success:
                    if order_balance_movements is not None:
                        result_data = self.format_data(order_balance_movements)
                        has_permission_view_payment_order_detail = check_permissions_by_user(self.request.user,
                                                                                             'CAN_VIEW_PAYMENT_ORDER_DETAIL')
                        for i in order_balance_movements:
                            i['has_permission_view_payment_order_detail'] = has_permission_view_payment_order_detail
                    else:
                        result_data = order_balance_movements
                    self.logger.info("Page: {}".format(page))
                    context.update(
                        {'search_count': page.get('total_elements', 0),
                         'list': result_data,
                         'summaries': summaries,
                         'choices': choices,
                         'sof_type_id': sof_type_id,
                         'sof_id': sof_id,
                         'order_detail_status': order_detail_status,
                         'order_detail_status_list': order_detail_status_list,
                         'cash_sof_list': cash_sof_list,
                         'paginator': page,
                         'page_range': calculate_page_range_from_page_info(page),
                         'agent_id': user_id,
                         'from_created_timestamp': from_created_timestamp,
                         'to_created_timestamp': to_created_timestamp,
                         'is_show_export': check_permissions_by_user(self.request.user, "CAN_EXPORT_AGENT_INDIVIDUAL_WALLET")
                         }
                    )
                else:
                    context.update(
                        {'search_count': 0,
                         'data': [],
                         'paginator': {},
                         'agent_id': user_id,
                         'is_show_export': False
                         }
                    )
                self.logger.info('Finish search agent transaction history')
        request.session['back_wallet_url'] = request.build_absolute_uri()
        self.logger.info('========== Finished getting agent transaction history ==========')
        return render(request, self.template_name, context)

    def _get_choices_types(self):
        url = settings.DOMAIN_NAMES + SOF_TYPES_URL
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())

        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)

        return {'sof_types': data}

    def _get_cash_sof_list(self, agent_id, user_type):
        self.logger.info('========== Start getting cash sof list ==========')
        body = {}
        body['user_id'] = int(agent_id)
        body['user_type'] = int(user_type)
        success, status_code, status_message, data = RestFulClient.post(url=CASH_SOFS_URL, headers=self._get_headers(),
                                                                        params=body, loggers=self.logger)

        data = data or {}
        API_Logger.post_logging(
            loggers=self.logger,
            params=body,
            response=data.get('cash_sofs', []),
            status_code=status_code,
            is_getting_list=True
        )

        self.logger.info('========== Finish getting cash sof list ==========')

        return data

    def _get_order_detail_status_list(self):
        data = []
        for key, value in ORDER_DETAIL_STATUS.items():
            temp = {"id" : key, "name": value}
            data.append(temp)
        return data

    def _get_transaction_history(self, body):
        order_balance_movements, page, success, status_message = self._get_transaction_history_list(body)
        if not success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            return order_balance_movements, page, [], success

        summary_body = body.copy()
        summary_body.pop('paging')
        summary_body.pop('page_index')

        summaries, success, status_message = self._get_transaction_history_summary(summary_body)
        if not success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )

        return order_balance_movements, page, summaries, success

    def _get_transaction_history_list(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.BALANCE_MOVEMENT_LIST_PATH,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body,
                                                                        timeout=settings.GLOBAL_TIMEOUT)
        data = data or {}
        order_balance_movements = data.get('order_balance_movements', [])
        page = data.get("page", {})
        API_Logger.post_logging(loggers=self.logger, params=body, response=order_balance_movements,
                                status_code=status_code, is_getting_list=True)
        return order_balance_movements, page, success, status_message

    def _get_transaction_history_summary(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.BALANCE_MOVEMENT_SUMMARY_PATH,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body,
                                                                        timeout=settings.GLOBAL_TIMEOUT)
        data = data or {}
        summaries = data.get('summaries', [])
        summaries = sorted(summaries, key=lambda value: value.get('currency'), reverse=False)
        API_Logger.post_logging(loggers=self.logger, params=body, response=summaries,
                                status_code=status_code, is_getting_list=True)

        return summaries, success, status_message

    def format_data(self, data):
        for i in data:
            i['order_status_name'] = ORDER_STATUS.get(i.get('order_status'))
            if i['order_status_name'] is None:
                i['order_status_name'] = 'Unknown({})'.format(i.get('order_status'))
            i['order_detail_status_name'] = ORDER_DETAIL_STATUS.get(i.get('order_detail_status'))
            if i['order_detail_status_name'] is None:
                i['order_detail_status_name'] = 'Unknown({})'.format(i.get('order_detail_status'))
            i['sof_type_name'] = SOF_TYPE.get(i['sof_type_id'])
        return data

    def _getWalletViewInDay(self):
        url = api_settings.CONFIGURATION_DETAIL_URL.format(scope=self.paymentScopeName,
                                                           key=self.walletViewTransactionHistoryInDaysKey)
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if success:
            return data.get("value")
        else:
            return None

    def _getDiffDaysFromUIDateValue(self, fromDate, toDate):
        from_created_timestamp_as_datetime = datetime.strptime(fromDate, self.dateUIFormat)
        to_created_timestamp_as_datetime = datetime.strptime(toDate, self.dateUIFormat)
        detal = to_created_timestamp_as_datetime - from_created_timestamp_as_datetime
        return detal.days
