import logging
from web_admin import api_settings
from django.shortcuts import render
from django.views.generic.base import TemplateView

from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

'''
Author: Unknown
History:
# 2017-05-18 (Steve Le)
- Refactored code following RESTfulMethods standard.
'''
class SearchView(TemplateView, RESTfulMethods):

    template_name = "list.html"

    def get(self, request):
        return render(request, 'list.html')

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search system user ==========')

        # Get params
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Build body
        body = {}
        if username is not '':
            body['username'] = username
        if email is not '':
            body['email'] = email

        api_path = api_settings.SEARCH_SYSTEM_USER

        data, status = self._post_method(
            api_path=api_path,
            func_description="Search System User",
            logger=logger,
            params=body
        )

        return render(request, 'list.html', {'data': data})

