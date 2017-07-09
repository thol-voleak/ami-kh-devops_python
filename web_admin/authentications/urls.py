from authentications.views.permissions.list import PermissionList
from authentications.views.permissions.create import PermissionCreate
from authentications.views.auth import login_user, logout_user

from django.conf.urls import url

app_name = 'authentications'

urlpatterns = [
    url(r'^logout/$', logout_user, name='logout'),
    url(r'^login/$', login_user, name='login'),
    url(r'^permissions/list$', PermissionList.as_view(), name='permissions_list'),
    url(r'^permissions/create$', PermissionCreate.as_view(), name='create_permission'),
]
