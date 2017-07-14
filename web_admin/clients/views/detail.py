import logging
from web_admin import api_settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger

logger = logging.getLogger(__name__)


class DetailView(TemplateView, RESTfulMethods):
    template_name = "clients/client_detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info("========== Start Getting client detail ==========")
        context = super(DetailView, self).get_context_data(**kwargs)
        client_id = context['client_id']

        client_info, success_info = self._get_client_detail(client_id)

        client_scopes, success_scope = self._get_client_scopes(client_id)
        context['client_info'] = client_info
        context['client_scopes'] = client_scopes
        self.logger.info("========== Finish Getting client detail ==========")
        return context

    def _get_client_scopes(self, client_id):
        url = api_settings.CLIENT_SCOPES.format(client_id=client_id)
        return self._get_method(url, 'client scopes', logger)

    def _get_client_detail(self, client_id):
        url = api_settings.CLIENTS_LIST_URL + '/' + client_id
        return self._get_method(url, 'client detail', logger)
