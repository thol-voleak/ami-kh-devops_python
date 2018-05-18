from django.views.generic.base import TemplateView
from web_admin.utils import build_logger, check_permissions
from .utils import get_label_levels

import logging

logger = logging.getLogger(__name__)


class TierLevelView(TemplateView):
    template_name = "services/tier_levels/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        check_permissions(request, "CAN_LABEL_TIER_CONFIGURATION")
        self.logger = build_logger(request, __name__)
        return super(TierLevelView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(TierLevelView, self).get_context_data(**kwargs)
        label_levels = get_label_levels(self.request)
        context['data'] = label_levels

        return context