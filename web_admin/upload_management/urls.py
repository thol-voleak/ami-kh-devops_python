from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from upload_management.views.list import FileList
from upload_management.views.download import Download

app_name = 'upload_management'

urlpatterns = [
    url(r'^$', login_required(FileList.as_view(), login_url='authentications:login'), name="list"),
    url(r'^download/(?P<file_id>[0-9]+)/(?P<status_id>[0-9]+)/$', login_required(Download.as_view(), login_url='authentications:login'), name="download")
]