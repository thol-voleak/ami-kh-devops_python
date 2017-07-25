from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView
from braces.views import GroupRequiredMixin

import logging

logger = logging.getLogger(__name__)


class ListView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "SYS_VIEW_LIST_BANK"
    login_url = 'web:web-index'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "bank/list.html"
    url = "api-gateway/report/"+api_settings.API_VERSION+"/banks"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get bank list ==========')
        data, success = self._post_method(self.url, "get bank list", logger)

        if success:
            self.logger.info('========== Finished get get bank list ==========')
            for i in data:
                i['is_permision_detail'] = check_permissions_by_user(self.request.user, 'SYS_VIEW_DETAIL_BANK')
                i['is_permision_edit'] = check_permissions_by_user(self.request.user, 'SYS_EDIT_BANK')
                i['is_permision_delete'] = check_permissions_by_user(self.request.user, 'SYS_DELETE_BANK')
            result = {'data': data}
            return result
