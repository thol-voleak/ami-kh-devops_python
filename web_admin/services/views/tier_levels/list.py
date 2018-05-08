from django.conf import settings
from web_admin import api_settings
from django.views.generic.base import TemplateView
from web_admin.utils import build_logger
from web_admin.restful_helper import RestfulHelper

import logging

logger = logging.getLogger(__name__)


class TierLablesView(TemplateView):
    template_name = "services/tier_levels/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = build_logger(request, __name__)
        return super(TierLablesView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(TierLablesView, self).get_context_data(**kwargs)
        label_levels = self.get_label_levels()
        context['data'] = label_levels

        return context

    def get_label_levels(self):
        success, status_code, message, data = RestfulHelper.send(
            method='GET',
            url=api_settings.TIER_LEVELS_LIST,
            params={},
            request=self.request,
            description='getting label levels list',
            log_count_field='data'
        )
        return data if success else {}
