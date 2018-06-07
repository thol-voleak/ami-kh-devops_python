from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView
from .views.create import SystemUserCreate
from .views.delete import DeleteView
from .views.detail import DetailView
from .views.update import SystemUserUpdateForm
from .views.change_password import SystemUserChangePassword
from .views.self_change_password import SelfChangePassword
from .views.user_role_management import RoleManagementView
from .views.update_status import suspend, activate


app_name = 'system_user'

urlpatterns = [
    url(r'^list/$', login_required(ListView.as_view(), login_url='authentications:login'), name="system-user-list"),
    url(r'^create/$', login_required(SystemUserCreate.as_view(), login_url='authentications:login'), name="create-system-user"),
    url(r'^(?P<system_user_id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'),
        name="delete-system-user"),
    url(r'^detail/(?P<systemUserId>[0-9]+)/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="system-user-detail"),
    url(r'^update/(?P<systemUserId>[0-9A-Za-z]+)/$', login_required(SystemUserUpdateForm.as_view(), login_url='authentications:login'),
        name="system-user-edit"),
    url(r'^(?P<systemUserId>[0-9A-Za-z]+)/change-password/$', login_required(SystemUserChangePassword.as_view(), login_url='authentications:login'),
        name="system-user-change-password"),
    url(r'^(?P<system_user_id>[0-9A-Za-z]+)/role-management/$', login_required(RoleManagementView.as_view(), login_url='authentications:login'),
        name="system_user_role_management"),
    url(r'^change-password/$', login_required(SelfChangePassword.as_view(), login_url='authentications:login'),
        name="self_change_password"),
    url(r'^suspend/(?P<system_user_id>[0-9A-Za-z]+)/$', login_required(suspend, login_url='authentications:login'),
        name="system_user_suspend"),
    url(r'^activate/(?P<system_user_id>[0-9A-Za-z]+)/$', login_required(activate, login_url='authentications:login'),
        name="system_user_activate"),
]
