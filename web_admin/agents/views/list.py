from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import SEARCH_AGENT
from web_admin.restful_methods import RESTfulMethods

from datetime import datetime
from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)

STATUS = {
    1: 'Active',
}


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_MANAGE_AGENT_REGISTRATION"
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

        # Build Body
        body = {}
        redirect_from_delete =  self.request.session.pop('agent_redirect_from_delete', None)
        if redirect_from_delete:
            unique_reference = self.request.session.pop('agent_unique_reference', None)
            email = self.request.session.pop('agent_email', None)
            primary_mobile_number = self.request.session.pop('agent_primary_mobile_number', None)
            kyc_status = self.request.session.pop('agent_kyc_status', None)
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

        context.update({'unique_reference': unique_reference,
                        'email': email,
                        'primary_mobile_number': primary_mobile_number,
                        'kyc_status': kyc_status})

        # Get Data
        data, success = self._get_agents(params=body)
        if not success:
            if data == 'timeout':
                context.update({'msgs': {'get_list_timeout': 'Search timeout, please try again'}})
                context['search_count'] = 0
        else:
            context['data'] = data
            context['search_count'] = len(data)

        self.update_session(request, None, unique_reference, email, primary_mobile_number, kyc_status,
                            from_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            to_created_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"), False)

        self.logger.info('========== Finished showing Agent List page ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        # Get params
        agent_id = request.POST.get('agent_id')
        unique_reference = request.POST.get('unique_reference')
        email = request.POST.get('email')
        primary_mobile_number = request.POST.get('primary_mobile_number')
        kyc_status = request.POST.get('kyc_status')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        # Build Body
        context = {}
        body = {}
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
        data, success = self._get_agents(params=body)
        if not success:
            if data == 'timeout':
                context.update({'msgs': {
                    'get_list_timeout': 'Search timeout, please try again'}})
                context['search_count'] = 0
        else:
            context['data'] = data
            context['search_count'] = len(data)

        self.update_session(request, None, unique_reference, email,
                            primary_mobile_number, kyc_status,
                            new_from_created_timestamp,
                            new_to_created_timestamp, False)
        return render(request, self.template_name, context)

    def _get_agents(self, params):
        self.logger.info('========== Start searching agent ==========')

        api_path = SEARCH_AGENT
        data, success = self._post_method(
            api_path=api_path,
            func_description="Search Agent",
            logger=logger,
            params=params
        )
        if success:
            is_permission_view = check_permissions_by_user(self.request.user, 'CAN_VIEW_AGENT')
            is_permission_edit = check_permissions_by_user(self.request.user, 'CAN_EDIT_AGENT_DETAILS')
            is_permission_delete = check_permissions_by_user(self.request.user, 'CAN_DELETE_AGENT')

            for i in data:
                i['is_permission_view'] = is_permission_view
                i['is_permission_edit'] = is_permission_edit
                i['is_permission_delete'] = is_permission_delete

        self.logger.info('========== Finished searching agent ==========')
        return data, success

    def update_session(self, request, message=None, unique_reference=None, email=None, primary_mobile_number=None,
                       kyc=None, from_created_timestamp=None, to_created_timestamp=None, redirect_from_delete=False):
        request.session['agent_message'] = message
        request.session['agent_unique_reference'] = unique_reference
        request.session['agent_email'] = email
        request.session['agent_primary_mobile_number'] = primary_mobile_number
        request.session['agent_kyc_status'] = kyc
        request.session['agent_from'] = from_created_timestamp
        request.session['agent_to'] = to_created_timestamp
        request.session['agent_redirect_from_delete'] = redirect_from_delete

