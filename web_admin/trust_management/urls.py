from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from trust_management.views.list import ListTrust
from trust_management.views.add import AddTrust
from trust_management.views.get_user_name import get_user_name

app_name = 'trust_management'

urlpatterns = [
    url(r'^$', login_required(ListTrust.as_view(), login_url='authentications:login'), name="list_trust"),
    url(r'^add/$', login_required(AddTrust.as_view(), login_url='authentications:login'), name="add_trust"),
    url(r'^get_user_name/$', login_required(get_user_name, login_url='authentications:login'), name="get_user_name")
]
