import logging

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView


from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class ClientUpdateForm(TemplateView, RESTfulMethods):
    template_name = "clients/update_client_form.html"

    def get_context_data(self, **kwargs):
        context = super(ClientUpdateForm, self).get_context_data(**kwargs)
        client_id = context['client_id']
        return self._get_client_detail(client_id)

    def _get_client_detail(self, client_id):

        url = settings.CLIENTS_LIST_URL + '/' + client_id
        data, success = self._get_method(url, 'Client Detail', logger)

        context = {'client_info': data,
                   'error_msg': None}
        return context


class ClientUpdate(TemplateView, RESTfulMethods):
    def post(self, request, *args, **kwargs):

        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')

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
            "autoapprove": ""
        }

        url = settings.UPDATE_CLIENT_URL.format(client_id)

        data, success = self._put_method(url, 'client', logger, params)

        if success:
            request.session['client_update_msg'] = 'Updated data successfully'
            return redirect('clients:client-list')
        else:
            context = {'client_info': params,
                       'error_msg': None}
            return render(request, 'clients/update_client_form.html', context)
