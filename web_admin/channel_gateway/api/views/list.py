from django.views.generic.base import TemplateView
import logging


logger = logging.getLogger(__name__)


class ListView(TemplateView):

    template_name = "channel-gateway-api/list.html"