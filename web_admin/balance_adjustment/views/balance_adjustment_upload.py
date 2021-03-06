# views.py
import logging
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadhandler import MemoryFileUploadHandler, \
    StopFutureHandlers, SkipFile

# class who handles the upload
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from io import BytesIO

import json

from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
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
        """
        Use the content_length to signal whether or not this handler should be in use.
        """
        # Check the content-length header to see if we should
        # If the post is too large, the program auto switch to TemporaryFileUploadHandler.
        if content_length > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            self.activated = False
            # TODO: Need to update uploaded size if implement temporary upload hander
            # upload_progress_<uuid> = {'length':<file_length>,'uploaded':<uploaded_size>}
        else:
            self.activated = True
        self.content_length = content_length
        self.progress_id = _get_cache_key(self.request)
        if self.progress_id:
            self.cache_key = self.progress_id
            self.request.session['upload_progress_%s' % self.cache_key] = {
                'length': self.content_length,
                'uploaded': 0
            }
    
    def new_file(self, *args, **kwargs):
        super(MemoryFileUploadHandler, self).new_file(*args, **kwargs)
        fileName = args[1]
        if not fileName.endswith('.csv'):
            self.request.session['wrong_file_type_%s' % self.cache_key] = True
            self.request.session.save()
            raise SkipFile("wrong_file_type:%s"%fileName)
        if self.activated:
            self.file = BytesIO()
            raise StopFutureHandlers()
    
    def receive_data_chunk(self, raw_data, start):
        if self.activated:
            data = self.request.session['upload_progress_%s' % self.cache_key]
            data['uploaded'] += self.chunk_size
            self.request.session['upload_progress_%s' % self.cache_key] = data
            self.request.session.save()
            self.file.write(raw_data)
        else:
            return raw_data  # data wont be passed to any other handler
        return None
    
    def file_complete(self, file_size):
        if not self.activated:
            return
        
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
    progress_id = _get_cache_key(request)
    if progress_id:
        cache_key = "%s" % (progress_id)
        data = request.session.get('upload_progress_%s' % cache_key, None)
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')


@csrf_exempt
def upload_form(request):
    if not check_permissions_by_user(request.user, 'CAN_UPLOAD_BALANCE_ADJUSTMENT'):
        return HttpResponse(json.dumps({'id': -1, "code": "permission_denied"}))
    request.upload_handlers.insert(0, ProgressUploadHandler(request))  # place our custom upload in first position
    return _upload_file_view(request)


# view thath launch the upload process
@csrf_protect
def _upload_file_view(request):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    if request.method == 'POST':
        upload_file = request.FILES.get('file_data', None)
        if (upload_file == None):
            is_wrong_file = request.session.get('wrong_file_type_%s' % _get_cache_key(request), None)
            del request.session['wrong_file_type_%s' % _get_cache_key(request)]
            request.session.save()

            if is_wrong_file:
                data = {'id': -1, "code": "Upload must be in csv format"}
                return HttpResponse(json.dumps(data))
        # 8MB = 1024 * 1024 * 8 = 8388608
        if upload_file.size > 8388608:
            data = {'id': -1, "code": "file_exceeded_max_size"}
        else:
            data = _upload_via_api(request, upload_file, 1, logger)
        return HttpResponse(json.dumps(data))

def _get_cache_key(request):
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    return progress_id

def _upload_via_api(request, file, function_id, logger):
    myHeader = get_auth_header(request.user)
    #

    myHeader["content-type"] = None
    myHeader["content-type"] = None
    myHeader["Content-Type"] = None
    is_success, status_code, status_message, data = RestFulClient.upload(url=UPLOAD_FILE, files={'file_data': file},
                                                                         headers=myHeader,
                                                                         loggers=logger,
                                                                         params={'function_id': function_id},
                                                                         timeout=settings.GLOBAL_TIMEOUT)
    
    API_Logger.post_logging(loggers=logger, params={'file_data': file._name, 'function_id': function_id}, response=data,
                            status_code=status_code, is_getting_list=True)
    
    if not is_success:
        data = []
    return data
