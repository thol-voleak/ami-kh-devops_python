from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.create import SystemUserCreate
from .views.delete import DeleteView
from .views.detail import DetailView
from .views.update import SystemUserUpdateForm
from .views.change_password import SystemUserChangePassword

app_name = 'system_user'

urlpatterns = [
    url(r'^list/$', login_required(ListView.as_view(), login_url='login'), name="system-user-list"),
    url(r'^create/$', login_required(SystemUserCreate.as_view(), login_url='login'), name="create-system-user"),
    url(r'^(?P<system_user_id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='login'),
        name="delete-system-user"),
    url(r'^detail/(?P<systemUserId>[0-9]+)/$', login_required(DetailView.as_view(), login_url='login'), name="system-user-detail"),
    url(r'^update/(?P<systemUserId>[0-9A-Za-z]+)/$', login_required(SystemUserUpdateForm.as_view(), login_url='login'),
        name="system-user-edit"),
    url(r'^(?P<systemUserId>[0-9A-Za-z]+)/change-password/$', login_required(SystemUserChangePassword.as_view(), login_url='login'),
        name="system-user-change-password")
]
