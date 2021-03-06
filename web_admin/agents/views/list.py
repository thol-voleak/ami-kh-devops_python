from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import SEARCH_AGENT
from web_admin.restful_methods import RESTfulMethods
from datetime import datetime
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)

STATUS = {
    1: 'Active',
}


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_VIEW_AGENT_LIST"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/list.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start showing Agent List page ==========')
        context = {
            'msgs':{
                'update_msg': self.request.session.pop('agent_update_msg', None),
                'del_msg': self.request.session.pop('agent_delete_msg', None)
            }
        }

        from_created_timestamp = datetime.now()
        to_created_timestamp = datetime.now()
        unique_reference = None
        email = None
        primary_mobile_number = None
        kyc_status = None
        agent_id = None
        edc_serial_number = None
        mobile_device_unique_reference = None

        # Build Body
        body = {}
        body['paging'] = True
        body['page_index'] = 1
        redirect_from_delete =  self.request.session.pop('agent_redirect_from_delete', None)

        redirect_from_wallet_view = self.request.session.pop('agent_redirect_from_wallet_view', None)
        if redirect_from_delete or redirect_from_wallet_view:
            agent_id = self.request.session.pop('agent_id', None)
            unique_reference = self.request.session.pop('agent_unique_reference', None)
            email = self.request.session.pop('agent_email', None)
            primary_mobile_number = self.request.session.pop('agent_primary_mobile_number', None)
            kyc_status = self.request.session.pop('agent_kyc_status', None)
            edc_serial_number = self.request.session.pop('edc_serial_number', None)
            mobile_device_unique_reference = self.request.session.pop('mobile_device_unique_reference', None)

            if request.session['agent_from'] != '':
                from_created_timestamp = datetime.strptime(request.session['agent_from'], "%Y-%m-%dT%H:%M:%SZ")
                new_from_created_timestamp = from_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                body['from_created_timestamp'] = new_from_created_timestamp
                new_from_created_timestamp = from_created_timestamp.strftime("%Y-%m-%d")
                context['from_created_timestamp'] = new_from_created_timestamp
            else:
                context['from_created_timestamp'] = ''
            if request.session['agent_to'] != '':
                to_created_timestamp = datetime.strptime(request.session['agent_to'], "%Y-%m-%dT%H:%M:%SZ")
                new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                body['to_created_timestamp'] = new_to_created_timestamp
                new_to_created_timestamp = to_created_timestamp.strftime("%Y-%m-%d")
                context['to_created_timestamp'] = new_to_created_timestamp
            else:
                context['to_created_timestamp'] = ''

            context.update({'msgs':{'delete_failed_msg': self.request.session.pop('agent_message', None)}})
        else:
            # Set first load default time for Context
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


        if agent_id:
            body.update({'id' : int(agent_id)})
            context.update({'id': int(agent_id)})
        if unique_reference:
            body.update({'unique_reference' : unique_reference})
        if email:
            body.update({'email' : email})
        if primary_mobile_number:
            body.update({'primary_mobile_number' : primary_mobile_number})
        if kyc_status:
            if kyc_status and isinstance(kyc_status, str):
                if kyc_status.lower() == "true":
                    body.update({'kyc_status': True})
                else:
                    body.update({'kyc_status': False})

        if edc_serial_number:
            body.update({'edc_serial_number': edc_serial_number})
        if mobile_device_unique_reference:
            body.update({'mobile_device_unique_reference': mobile_device_unique_reference})

        context.update({'unique_reference': unique_reference,
                        'email': email,
                        'primary_mobile_number': primary_mobile_number,
                        'edc_serial_number': edc_serial_number,
                        'mobile_device_unique_reference': mobile_device_unique_reference,
                        'kyc_status': body.get('kyc_status', None),
                        'has_permission_search': check_permissions_by_user(self.request.user,"CAN_SEARCH_AGENT")
                        })

        # Get Data
        data, success, status_message = self._get_agents(params=body)
        if not success:
            if status_message == 'timeout':
                context.update({'msgs': {'get_list_timeout': 'Search timeout, please try again'}})
                context['search_count'] = 0
        else:
            agents_list = data.get("agents", [])

            page = data.get("page", {})
            context.update(
                {'search_count': page.get('total_elements', 0), 'data': agents_list, 'paginator': page,
                 'page_range': calculate_page_range_from_page_info(page)})

        self.update_session(request, None, agent_id, unique_reference, email, primary_mobile_number, kyc_status,
                            edc_serial_number, mobile_device_unique_reference,
                            from_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            to_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"), False, False)

        self.logger.info('========== Finished showing Agent List page ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not check_permissions_by_user(request.user, 'CAN_SEARCH_AGENT'):
            return render(request, 'web/permission-denied.html')
        # Get params
        agent_id = request.POST.get('agent_id')
        unique_reference = request.POST.get('unique_reference')
        email = request.POST.get('email')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        kyc_status = request.POST.get('kyc_status')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        opening_page_index = request.POST.get('current_page_index')
        edc_serial_number = request.POST.get('edc_serial_number')
        mobile_device_unique_reference = request.POST.get('mobile_device_unique_reference')

        # Build Body
        context = {}
        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        if agent_id:
            body['id'] = int(agent_id)
        if unique_reference:
            body['unique_reference'] = unique_reference
        if email:
            body['email'] = email
        if primary_mobile_number:
            body['primary_mobile_number'] = primary_mobile_number

        if kyc_status and isinstance(kyc_status, str):
            if kyc_status.lower() == "true":
                new_kyc_status = True
            else:
                new_kyc_status = False
            body['kyc_status'] = new_kyc_status
            context['kyc_status'] = kyc_status

        if edc_serial_number:
            body['edc_serial_number'] = edc_serial_number
        if mobile_device_unique_reference:
            body['mobile_device_unique_reference'] = mobile_device_unique_reference

        context.update(body)

        new_from_created_timestamp = ''
        if from_created_timestamp is not '':
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp
            context['from_created_timestamp'] = from_created_timestamp

        new_to_created_timestamp = ''
        if to_created_timestamp is not '':
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp
            context['to_created_timestamp'] = to_created_timestamp

        # Get Data
        data, success, status_message = self._get_agents(params=body)
        if not success:
            if status_message == 'timeout':
                context.update({'msgs': {
                    'get_list_timeout': 'Search timeout, please try again'}})
                context['search_count'] = 0
        else:
            agents_list = data.get("agents", [])
            page = data.get("page", {})
            context.update(
                {'search_count': page.get('total_elements', 0), 'data': agents_list, 'paginator': page, 'page_range': calculate_page_range_from_page_info(page)})
        context['has_permission_search'] = check_permissions_by_user(self.request.user, "CAN_SEARCH_AGENT")
        self.update_session(request, None, agent_id, unique_reference, email,
                            primary_mobile_number, kyc_status, edc_serial_number, mobile_device_unique_reference,
                            new_from_created_timestamp,
                            new_to_created_timestamp, False, False)
        return render(request, self.template_name, context)

    def _get_agents(self, params):
        self.logger.info('========== Start searching agent ==========')

        api_path = SEARCH_AGENT
        success, status_code, status_message, data = RestFulClient.post(
            url=api_path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=params, response=data.get('agents', []),
                                status_code=status_code, is_getting_list=True)

        if success:
            has_permission_view = check_permissions_by_user(self.request.user, 'CAN_VIEW_AGENT')
            has_permission_edit = check_permissions_by_user(self.request.user, 'CAN_EDIT_AGENT_DETAILS')
            has_permission_delete = check_permissions_by_user(self.request.user, 'CAN_DELETE_AGENT')
            has_permission_identity = check_permissions_by_user(self.request.user, 'CAN_VIEW_AGENT_IDENTITIES')
            has_permission_smartcard = check_permissions_by_user(self.request.user, 'CAN_VIEW_AGENT_SMARTCARD')
            has_permission_sofcash = check_permissions_by_user(self.request.user, 'CAN_VIEW_AGENT_SOFCASH')
            has_permission_sofbank = check_permissions_by_user(self.request.user, 'CAN_VIEW_AGENT_SOFBANK')
            has_permission_suspend = check_permissions_by_user(self.request.user, 'CAN_SUSPEND_AGENTS')
            has_permission_individual_wallet = check_permissions_by_user(self.request.user, 'CAN_VIEW_AGENT_INDIVIDUAL_WALLET')
            has_permission_management = self.check_membership(['CAN_VIEW_PROFILE_MANAGEMENT'])
            agents = data.get('agents', [])
            for i in agents:
                i['has_permission_view'] = has_permission_view
                i['has_permission_edit'] = has_permission_edit
                i['has_permission_delete'] = has_permission_delete
                i['has_permission_identity'] = has_permission_identity
                i['has_permission_individual_wallet'] = has_permission_individual_wallet
                i['has_permission_smartcard'] = has_permission_smartcard
                i['has_permission_sofcash'] = has_permission_sofcash
                i['has_permission_sofbank'] = has_permission_sofbank
                i['has_permission_suspend'] = has_permission_suspend
                i['has_permission_management'] = has_permission_management

        self.logger.info('========== Finished searching agent ==========')
        return data, success, status_message

    def update_session(self, request, message=None,id=None , unique_reference=None, email=None, primary_mobile_number=None,
                       kyc=None, edc_serial_number=None, mobile_device_unique_reference=None, from_created_timestamp=None, to_created_timestamp=None, redirect_from_delete=False, redirect_from_wallet_view = False):
        request.session['agent_message'] = message
        request.session['agent_id'] = id
        request.session['agent_unique_reference'] = unique_reference
        request.session['agent_email'] = email
        request.session['agent_primary_mobile_number'] = primary_mobile_number
        request.session['agent_kyc_status'] = kyc
        request.session['edc_serial_number'] = edc_serial_number
        request.session['mobile_device_unique_reference'] = mobile_device_unique_reference
        request.session['agent_from'] = from_created_timestamp
        request.session['agent_to'] = to_created_timestamp
        request.session['agent_redirect_from_delete'] = redirect_from_delete
        request.session['agent_redirect_from_wallet_view'] = redirect_from_wallet_view

