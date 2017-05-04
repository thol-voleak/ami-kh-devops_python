from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AgentUpdate(TemplateView):
    template_name = "update.html"
