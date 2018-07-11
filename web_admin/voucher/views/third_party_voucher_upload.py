# views.py
import logging

# class who handles the upload
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

import json

from authentications.utils import get_correlation_id_from_username
from balance_adjustment.views import balance_adjustment_upload as common_upload
from balance_adjustment.views.balance_adjustment_upload import ProgressUploadHandler
from web_admin import setup_logger

class ThirdPartyUploadHandler(ProgressUploadHandler):
    pass

# view that display the current upload progress (json)
def upload_progress(request):
    return common_upload.upload_progress(request);

@csrf_exempt
def upload_form(request):
    request.upload_handlers.insert(0, ThirdPartyUploadHandler(request))  # place our custom upload in first position
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
            is_wrong_file = request.session.get('wrong_file_type_%s' % common_upload._get_cache_key(request), None)
            del request.session['wrong_file_type_%s' % common_upload._get_cache_key(request)]
            request.session.save()

            if is_wrong_file:
                data = {'id': -1, "code": "Upload must be in csv format"}
                return HttpResponse(json.dumps(data))
        # 8MB = 1024 * 1024 * 8 = 8388608
        if upload_file.size > 8388608:
            data = {'id': -1, "code": "file_exceeded_max_size"}
        else:
            data = common_upload._upload_via_api(request, upload_file, 2, logger)
        return HttpResponse(json.dumps(data))
