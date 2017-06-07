from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.conf import settings
from web_admin import api_settings
import logging
from django.contrib import messages
from web_admin.restful_methods import RESTfulMethods
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

logger = logging.getLogger(__name__)

class SystemUserChangePassword(TemplateView, RESTfulMethods):
    template_name = "system_user/system_user_change_password.html"

    def get_context_data(self, **kwargs):
        try:

            context = super(SystemUserChangePassword, self).get_context_data(**kwargs)
            system_user_id = context['systemUserId']

            system_user_info = {
                "id": system_user_id,
                "password": None,
            }
            context = {'system_user_info': system_user_info}
            return context

        except:
            context = {'system_user_info': {}}
            return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start changing system user password ==========')
        system_user_id = kwargs['systemUserId']
        url = api_settings.SYSTEM_USER_CHANGE_PASSWORD_URL.format(system_user_id)
        password = request.POST.get('newpassword')

        message = password.encode('utf-8')
        # pub_key = RSA.importKey(open('/data/projects/admin-portal/config/rsa_public.pem').read())
        pub_key = RSA.importKey(open(settings.RSA).read())
        cipher = PKCS1_v1_5.new(pub_key)
        ciphertext = base64.encodestring(cipher.encrypt(message))
        password = ciphertext.decode('utf-8')

        params = {"password": password}
        data, success = self._put_method(api_path=url,
                                         func_description="password",
                                         logger=logger,
                                         params=params)
        logger.info('========== Finish changing system user password ==========')
        if success:
            messages.add_message(request, messages.SUCCESS, 'Password has been changed successfully')
            return redirect('system_user:system-user-list')
        else:
            context = {'system_user_info': params}
            return render(request, 'system_user/system_user_change_password.html', context)



        