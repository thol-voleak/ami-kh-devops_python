from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from django.conf import settings
from web_admin.api_settings import UPLOAD_URL

import requests
logger = logging.getLogger(__name__)


class Upload(TemplateView, GetHeaderMixin):
	template_name = "upload.html"
	login_url = 'web:permission_denied'
	logger = logger

	def dispatch(self, request, *args, **kwargs):
		correlation_id = get_correlation_id_from_username(self.request.user)
		self.logger = setup_logger(self.request, logger, correlation_id)
		return super(Upload, self).dispatch(request, *args, **kwargs)

	def check_membership(self, permission):
		self.logger.info(
			"Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
		return check_permissions_by_user(self.request.user, permission[0])

	def get(self, request, *args, **kwargs):
		self.logger.info('========== Start get upload details ==========')
		context = super(Upload, self).get_context_data(**kwargs)

		return render(request, self.template_name, context)

	def post(self, request):
		myHeader = self._get_headers()
		myHeader['content-type'] = None
		if request.FILES['file_data']:
			myfile = request.FILES['file_data']
			# files = {'file': open(myfile, 'rb')}
			# headers = self._get_headers()
			# headers["content-type"]='text/plain; charset=US-ASCII'
			# headers["content-type"]=''
			# headers["content-type"]=''


			is_success, status_code, status_message, data = RestFulClient.upload(url=UPLOAD_URL,
																				 headers=myHeader,
																				 loggers=self.logger,
																				 params={'function_id': 1},
																				 timeout=settings.GLOBAL_TIMEOUT,
																				 files={'file_data': myfile})

			# response = requests.post(url, files=files, headers=headers, data=params, verify=settings.CERT,
			# 						 timeout=timeout)
			self.logger.info("==================11111111============")
			context ={}
			context['uploaded_file_url'] = data
			self.logger.info(response)
		return render(request, 'upload.html',context)
