from django.views.generic.base import TemplateView
import logging

logger = logging.getLogger(__name__)


class EditView(TemplateView):
    template_name = "channel-gateway-api/edit.html"