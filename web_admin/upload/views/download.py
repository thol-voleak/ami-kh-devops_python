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
from web_admin.api_settings import DOWNLOAD_URL
from django.http import JsonResponse
from django.http import HttpResponse
from wsgiref.util import FileWrapper
import json

import requests
logger = logging.getLogger(__name__)


class Download(TemplateView, GetHeaderMixin):
	login_url = 'web:permission_denied'
	logger = logger

	def dispatch(self, request, *args, **kwargs):
		correlation_id = get_correlation_id_from_username(self.request.user)
		self.logger = setup_logger(self.request, logger, correlation_id)
		return super(Download, self).dispatch(request, *args, **kwargs)

	def check_membership(self, permission):
		self.logger.info(
			"Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
		return check_permissions_by_user(self.request.user, permission[0])

	def post(self, request, *args, **kwargs):
		headers = self._get_headers()
		file_id = request.POST.get('file_id')
		params = {'file_id': int(file_id), 'status_id': 2}

		data = RestFulClient.download(url=DOWNLOAD_URL, headers=headers, loggers=self.logger, params=params,timeout=settings.GLOBAL_TIMEOUT)
		response = HttpResponse(data.content, content_type='text/csv')
		response['Content-Disposition']='attachment; filename=abc.csv'
		return response
