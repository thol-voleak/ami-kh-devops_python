from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.upload import Upload
from .views.download import Download



app_name = 'upload'

urlpatterns = [
    url(r'^$', login_required(Upload.as_view(), login_url='authentications:login'), name="upload"),
    url(r'^download$', login_required(Download.as_view(), login_url='authentications:login'), name="download"),

]