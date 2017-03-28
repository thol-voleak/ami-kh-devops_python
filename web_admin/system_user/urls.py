from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.create import SystemUserCreate
from .views.delete import DeleteView

app_name = 'system_user'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="system-user-list"),
    url(r'^create/$', login_required(SystemUserCreate.as_view(), login_url='login'), name="create-system-user"),
    url(r'^(?P<system_user_id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='login'),
        name="delete-system-user"),
]
