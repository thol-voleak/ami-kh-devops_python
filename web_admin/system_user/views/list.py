import logging
from web_admin import api_settings
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.utils import setup_logger
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):

    template_name = "system_user/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        context = {
            'data': [],
            'created_msg': self.request.session.pop('system_user_create_msg', None),
            'del_msg': self.request.session.pop('system_user_delete_msg', None),
            'pw_msg': self.request.session.pop('system_user_change_password_msg', None)
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.logger.info("========== Start searching system user ==========")
        username = request.POST.get('username')
        email = request.POST.get('email')
        params = {}
        if username:
            params['username'] = username
        if email:
            params['email'] = email

        data = self._search_system_user(params)
        context['data'] = data
        context['username'] = username
        context['email'] = email
        self.logger.info("========== Finish searching system user ==========")
        return render(request, self.template_name, context)

    def _search_system_user(self, params):
        api_path = api_settings.SEARCH_SYSTEM_USER

        data, success = self._post_method(
            api_path=api_path,
            func_description="System User",
            logger=logger,
            params=params
        )
        return data
