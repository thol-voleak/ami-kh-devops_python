from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from upload_management.views.list import FileList

app_name = 'upload_management'

urlpatterns = [
    url(r'^$', login_required(FileList.as_view(), login_url='authentications:login'), name="list"),
]