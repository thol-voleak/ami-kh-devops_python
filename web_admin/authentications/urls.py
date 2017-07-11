from authentications.views.permissions.list import PermissionList
from authentications.views.permissions.create import PermissionCreate
from authentications.views.permissions.edit import PermissionEditView
from authentications.views.permissions.detail import PermissionDetailView
from authentications.views.permissions.delete import PermissionDeleteView
from authentications.views.roles.list import RoleList
from authentications.views.roles.create import RoleCreate
from authentications.views.roles.delete import RoleDeleteView
from authentications.views.roles.detail import RoleDetailView
from authentications.views.roles.edit import RoleEditView
from django.contrib.auth.decorators import login_required
from authentications.views.auth import login_user, logout_user

from django.conf.urls import url

app_name = 'authentications'

urlpatterns = [
    url(r'^logout/$', logout_user, name='logout'),
    url(r'^login/$', login_user, name='login'),
    url(r'^permissions/list$', login_required(PermissionList.as_view(), login_url='authentications:login'), name="permissions_list"),
    url(r'^permissions/create$', login_required(PermissionCreate.as_view(), login_url='authentications:login'), name="create_permission"),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/edit$', login_required(PermissionEditView.as_view(), login_url='authentications:login'), name="edit_permission"),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/delete$', login_required(PermissionDeleteView.as_view(), login_url='authentications:login'), name="delete_permission"),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/details$', login_required(PermissionDetailView.as_view(), login_url='authentications:login'), name="permission_detail"),

    url(r'^roles/list$', login_required(RoleList.as_view(), login_url='authentications:login'), name="role_list"),
    url(r'^roles/create$', login_required(RoleCreate.as_view(), login_url='authentications:login'), name="create_role"),
    url(r'^roles/(?P<role_id>[0-9A-Za-z]+)/edit$', login_required(RoleEditView.as_view(), login_url='authentications:login'), name="edit_role"),
    url(r'^roles/(?P<role_id>[0-9A-Za-z]+)/delete$', login_required(RoleDeleteView.as_view(), login_url='authentications:login'), name="delete_role"),
    url(r'^roles/(?P<role_id>[0-9A-Za-z]+)/details$', login_required(RoleDetailView.as_view(), login_url='authentications:login'), name="role_detail"),

]
