from authentications.views.permissions.list import PermissionList
from authentications.views.permissions.create import PermissionCreate
from authentications.views.permissions.edit import PermissionEditView
from authentications.views.permissions.detail import PermissionDetailView
from authentications.views.auth import login_user, logout_user

from django.conf.urls import url

app_name = 'authentications'

urlpatterns = [
    url(r'^logout/$', logout_user, name='logout'),
    url(r'^login/$', login_user, name='login'),
    url(r'^permissions/list$', PermissionList.as_view(), name='permissions_list'),
    url(r'^permissions/create$', PermissionCreate.as_view(), name='create_permission'),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/edit$', PermissionEditView.as_view(), name='edit_permission'),
    url(r'^permissions/(?P<permission_id>[0-9A-Za-z]+)/details', PermissionDetailView.as_view(),
        name='permission_detail'),
]
