from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "client_credentials/index.html"

    def get_context_data(self, **kwargs):
        pass
