from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from shop_category.views.create import CreateView
from shop_category.views.delete import DeleteView
from shop_category.views.detail import DetailView
from shop_category.views.edit import EditView
from shop_category.views.list import ListView

app_name = 'shop_category'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="shop_category_list"),
    url(r'^create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="shop_category_create"),
    url(r'^(?P<id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="shop_category_edit"),
    url(r'^(?P<id>[0-9A-Za-z]+)/detail/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="shop_category_detail"),
    url(r'^(?P<id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'), name="shop_category_delete"),
]
