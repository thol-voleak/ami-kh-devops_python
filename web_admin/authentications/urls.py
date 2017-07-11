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
    url(r'^permissions/create$', PermissionCreate.as_view(), name='create_permission'),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/edit$', PermissionEditView.as_view(), name='edit_permission'),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/delete', PermissionDeleteView.as_view(), name='delete_permission'),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/details', PermissionDetailView.as_view(),
        name='permission_detail'),

    url(r'^roles/list$', RoleList.as_view(), name='role_list'),
    url(r'^roles/create$', RoleCreate.as_view(), name='create_role'),
    url(r'^roles/(?P<role_id>[0-9A-Za-z]+)/edit$', RoleEditView.as_view(), name='edit_role'),
    url(r'^roles/(?P<role_id>[0-9A-Za-z]+)/delete', RoleDeleteView.as_view(), name='delete_role'),
    url(r'^roles/(?P<role_id>[0-9A-Za-z]+)/details', RoleDetailView.as_view(),
        name='role_detail'),
]
