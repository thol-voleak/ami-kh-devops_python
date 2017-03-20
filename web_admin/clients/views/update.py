from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings
import requests, random, string, time
from authentications.models import Authentications
from .detail import DetailView
import copy

from authentications.models import *

import logging

logger = logging.getLogger(__name__)


class ClientUpdateForm(TemplateView):
    template_name = "clients/update_client_form.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting client detail ==========')

            context = super(ClientUpdateForm, self).get_context_data(**kwargs)
            client_id = context['client_id']
            logger.info('client_id: ' + client_id)
            logger.info('========== Finished getting client detail ==========')

            return self._get_client_detail(client_id)
        except:
            context = {'client_info': {},
                       'error_msg': 'Sorry, we cannot get client detail.'}

            return context

    def _get_client_detail(self, client_id):

        url = settings.CLIENTS_LIST_URL + '/' + client_id
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        auth = Authentications.objects.get(user=self.request.user)
        access_token = auth.access_token

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer ' + access_token,
        }

        logger.info('Getting client detail from backend')
        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
        logger.info("Get client url: {}".format(url))
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))

        logger.info("Received data with response status is {}".format(response.status_code))

        response_json = response.json()
        if response_json['status']['code'] == "success":
            logger.info("Client detail was fetched.")
            data = response_json.get('data')
            context = {'client_info': data,
                       'error_msg': None}
            return context
        else:
            logger.info("Error Getting Client Detail.")
            context = {'client_info': response_json.get('data'),
                       'error_msg': response_json['status']['message']}

            return context


class ClientUpdate(View):
    @staticmethod
    def post(request, *args, **kwargs):

        logger.info('========== Start updating new client ==========')
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')

        logger.info('The Client to be updated {} client id.'.format(client_id))

        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": request.POST.get('client_name'),
            "scope": request.POST.get('scope'),
            "authorized_grant_types": request.POST.get('authorized_grant_types'),
            "web_server_redirect_uri": request.POST.get('web_server_redirect_uri'),
            "authorities": "",
            "access_token_validity": request.POST.get('access_token_validity'),
            "refresh_token_validity": request.POST.get('refresh_token_validity'),
            "additional_information": "",
            "resource_ids": "",
            "authorities": "",
            "autoapprove": ""
        }

        try:
            url = settings.UPDATE_CLIENT_URL.format(client_id)
            auth = Authentications.objects.get(user=request.user)
            access_token = auth.access_token

            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            headers = {
                'content-type': 'application/json',
                'correlation-id': correlation_id,
                'client_id': settings.CLIENTID,
                'client_secret': settings.CLIENTSECRET,
                'Authorization': 'Bearer {}'.format(access_token),
            }

            data_log = copy.deepcopy(params)
            data_log['client_secret'] = ''
            logger.info("Client info to be updated {}".format(data_log))

            start_date = time.time()
            response = requests.put(url, headers=headers, json=params, verify=False)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))

            response_json = response.json()
            status = response_json['status']

            logger.info("Response Code is {}".format(status['code']))

            if response.status_code == 200:
                if status['code'] == "success":
                    logger.info("Client was updated.")
                    logger.info('========== Finish updating client ==========')
                    request.session['client_update_msg'] = 'Updated data successfully'
                    return redirect('clients:client-list')
                else:
                    logger.info("Error Updating Client {}".format(client_id))
                    context = {'client_info': params,
                               'error_msg': response_json['status']['message']}
                    logger.info('========== Finish updating client ==========')
                    return render(request, 'clients/update_client_form.html', context)
            else:
                logger.info("Error Updating Client {}".format(client_id))
                logger.info("Status code {}".format(response.status_code))
                context = {'client_info': params,
                           'error_msg': '' + response.status_code}
                logger.info('========== Finish updating client ==========')
                return render(request, 'clients/update_client_form.html', context)

        except Exception as e:
            logger.info(e)
            logger.info('client_id: ' + client_id)
            context = {'client_info': params,
                       'error_msg': None}
            logger.info('========== Finish updating client ==========')
            return render(request, 'clients/update_client_form.html', context)
