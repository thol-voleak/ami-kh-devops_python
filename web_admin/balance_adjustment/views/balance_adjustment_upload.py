# views.py
import os

import logging
import simplejson
from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadhandler import MemoryFileUploadHandler, \
    StopFutureHandlers

# class who handles the upload
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from io import BytesIO

from rest_framework.utils import json

from authentications.utils import get_auth_header, get_correlation_id_from_username
from web_admin import RestFulClient
from web_admin import settings
from web_admin import setup_logger
from web_admin.api_logger import API_Logger
from web_admin.api_settings import UPLOAD_FILE


class ProgressUploadHandler(MemoryFileUploadHandler):
    """
    Download the file and store progression in the session
    """

    def __init__(self, request=None):
        super(ProgressUploadHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None
        self.request = request
        self.outPath = None
        self.destination = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        elif 'X-Progress-ID' in self.request.META:
            self.progress_id = self.request.META['X-Progress-ID']
        if self.progress_id:
            self.cache_key = self.progress_id
            self.request.session['upload_progress_%s' % self.cache_key] = {
                'length': self.content_length,
                'uploaded': 0
            }

    def new_file(self, *args, **kwargs):
        super(MemoryFileUploadHandler, self).new_file(*args, **kwargs)
        self.file = BytesIO()
        raise StopFutureHandlers()

    def receive_data_chunk(self, raw_data, start):
        data = self.request.session['upload_progress_%s' % self.cache_key]
        data['uploaded'] += self.chunk_size
        self.request.session['upload_progress_%s' % self.cache_key] = data
        self.request.session.save()
        self.file.write(raw_data)
        # data wont be passed to any other handler
        return None

    def file_complete(self, file_size):

        self.file.seek(0)
        return InMemoryUploadedFile(
            file=self.file,
            field_name=self.field_name,
            name=self.file_name,
            content_type=self.content_type,
            size=file_size,
            charset=self.charset,
            content_type_extra=self.content_type_extra
        )

    def upload_complete(self):
        try:
            self.destination.close()
        except:
            pass
        del self.request.session['upload_progress_%s' % self.cache_key]
        self.request.session.save()


# view that display the current upload progress (json)
def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        cache_key = "%s" % (progress_id)
        data = request.session.get('upload_progress_%s' % cache_key, None)
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')


@csrf_exempt
def upload_form(request):
    request.upload_handlers.insert(0, ProgressUploadHandler(request))  # place our custom upload in first position
    return _upload_file_view(request)

# view thath launch the upload process
@csrf_protect
def _upload_file_view(request):
    if request.method == 'POST':
        upload_file = request.FILES.get('file_data', None)  # start the upload
        data = _upload_via_api(request, upload_file)
        return HttpResponse(json.dumps(data))

def _upload_via_api(request, file):
    myHeader = get_auth_header(request.user)
    #
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)

    myHeader["content-type"] = None
    myHeader["content-type"] = None
    myHeader["Content-Type"] = None
    is_success, status_code, status_message, data = RestFulClient.upload(url=UPLOAD_FILE,files={'file_data': file},
                                                                         headers=myHeader,
                                                                         loggers= logger,
                                                                         params={'function_id': 1},
                                                                         timeout=settings.GLOBAL_TIMEOUT)

    API_Logger.post_logging(loggers=logger, params={'file_data': file._name}, response=data,
                            status_code=status_code, is_getting_list=True)

    if not is_success:
        # messages.add_message(
        #     request,
        #     messages.ERROR,
        #     status_message
        # )
        data = []
    return data
