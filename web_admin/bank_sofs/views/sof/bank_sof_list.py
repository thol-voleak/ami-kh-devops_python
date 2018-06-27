from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_logger import API_Logger
from datetime import date, timedelta
from django.views.generic.base import TemplateView
from django.shortcuts import render
from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info, make_download_file, export_file, convert_string_to_date_time
from web_admin import api_settings, setup_logger, RestFulClient
import logging

logger = logging.getLogger(__name__)


class BankSOFView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_SEARCH_BANK_SOF_CREATION"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "sof/bank_sof.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BankSOFView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # type: (object, object, object) -> object
        context = {"search_count": 0}
        self.initSearchDateTime(context)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start {} bank SOF =========='.format("downloading" if 'download' in request.POST else "searching"))

        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type_id')
        currency = request.POST.get('currency')
        created_from_date = request.POST.get('created_from_date')
        created_to_date = request.POST.get('created_to_date')
        created_from_time = request.POST.get('created_from_time')
        created_to_time = request.POST.get('created_to_time')
        opening_page_index = request.POST.get('current_page_index')

        body = {'paging': True, 'page_index': int(opening_page_index)}
        if user_id is not '' and user_id is not None:
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not '0' and user_type_id is not None:
            body['user_type_id'] = int(0 if user_type_id is None else user_type_id)
        if currency is not '' and currency is not None:
            body['currency'] = currency
        if created_from_date:
            body['from_created_timestamp'] = convert_string_to_date_time(created_from_date, created_from_time)
        if created_to_date:
            body['to_created_timestamp'] = convert_string_to_date_time(created_to_date, created_to_time)

        context = {}
        if 'download' in request.POST:
            file_type = request.POST.get('export-type')
            body['file_type'] = file_type
            body['row_number'] = 5000
            is_success, data = export_file(self, body=body, url_download=api_settings.BANK_SOFS_URL, api_logger=API_Logger)
            if is_success:
                response = make_download_file(data, file_type)
                self.logger.info('========== Finish exporting bank SOF ==========')
                return response
        else:
            data, success, status_message = self._get_bank_sof_list(body=body)

            context.update({
                'created_from_date': created_from_date,
                'created_to_date': created_to_date,
                'created_from_time': created_from_time,
                'created_to_time': created_to_time,
                'search_by': body
            })

            if success:
                cards_list = data.get("bank_sofs", [])
                page = data.get("page", {})
                self.logger.info("Page: {}".format(page))
                context.update({
                     'search_count': page.get('total_elements', 0),
                     'paginator': page,
                     'page_range': calculate_page_range_from_page_info(page),
                     'bank_sof_list': cards_list,
                     'is_show_export': check_permissions_by_user(self.request.user, 'CAN_EXPORT_BANK_SOF_INFORMATION')
                })

            else:
                context.update({
                     'search_count': 0,
                     'paginator': {},
                     'bank_sof_list': [],
                     'is_show_export': False
                })

            self.logger.info('========== End searching bank SOF ==========')
            return render(request, self.template_name, context)

    def _get_bank_sof_list(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=api_settings.BANK_SOFS_URL,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body)
        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('bank_sofs', []),
                                status_code=status_code, is_getting_list=True)
        return data, success, status_message

    def initSearchDateTime(self, context):
        today = date.today()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)
        context['created_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['created_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['created_from_time'] = "00:00:00"
        context['created_to_time'] = "00:00:00"
