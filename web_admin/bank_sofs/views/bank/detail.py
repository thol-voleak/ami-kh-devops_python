from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods

from django.conf import settings
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin

import logging

logger = logging.getLogger(__name__)


class DetailsView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "SYS_VIEW_DETAIL_BANK"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "bank/detail.html"
    get_bank_sof_detail_url = settings.DOMAIN_NAMES + "api-gateway/report/"+api_settings.API_VERSION+"/banks"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get bank detail ==========')
        context = super(DetailsView, self).get_context_data(**kwargs)
        bank_id = context['bank_id']
        self.logger.info("Get bank detail with [{}] bank Id".format(bank_id))
        bank = self._get_bank_details(bank_id)
        context = {'bank': bank}
        self.logger.info('========== Finished get bank detail ==========')
        return context

    def _get_bank_details(self, bank_id):
        params = {
            'id': bank_id
        }
        data, success = self._post_method(self.get_bank_sof_detail_url,
                                          "bank detail from backend",
                                          logger,
                                          params=params)

        if success:
            return data[0]
