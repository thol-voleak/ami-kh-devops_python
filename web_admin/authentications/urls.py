from django.conf.urls import url
from authentications.views import login_user, logout_user

app_name = 'authentications'

urlpatterns = [
    url(r'^logout/$', logout_user, name='logout'),
    url(r'^login/$', login_user, name='login')
]
