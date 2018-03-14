from web_admin.restful_methods import RESTfulMethods
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class CreateView(TemplateView, RESTfulMethods):
    template_name = "product/create.html"
