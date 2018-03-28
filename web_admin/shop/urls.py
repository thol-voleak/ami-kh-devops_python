from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.create import CreateView
from .views.delete import DeleteView
from .views.detail import DetailView
from .views.edit import EditView
from .views.list import ListView

app_name = 'shop'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="shop_list"),
    url(r'^create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="shop_create"),
    url(r'^(?P<id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="shop_edit"),
    url(r'^(?P<id>[0-9A-Za-z]+)/detail/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="shop_detail"),
    url(r'^(?P<id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'), name="shop_delete"),
]
