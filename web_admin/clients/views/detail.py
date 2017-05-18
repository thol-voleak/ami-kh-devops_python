import logging

from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class DetailView(TemplateView, RESTfulMethods):
    template_name = "clients/client_detail.html"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        client_id = context['client_id']

        client_info, success_info = self._get_client_detail(client_id)

        client_scopes, success_scope = self._get_client_scopes(client_id)
        context['client_info'] = client_info
        context['client_scopes'] = client_scopes
        return context

    def _get_client_scopes(self, client_id):
        url = settings.CLIENT_SCOPES.format(client_id=client_id)
        return self._get_method(url, 'client scopes', logger, True)

    def _get_client_detail(self, client_id):
        url = settings.CLIENTS_LIST_URL + '/' + client_id
        return self._get_method(url, 'client detail', logger)
