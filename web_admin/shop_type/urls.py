from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from shop_type.views.create import CreateView
from shop_type.views.delete import DeleteView
from shop_type.views.detail import DetailView
from shop_type.views.edit import EditView
from shop_type.views.list import ShopTypeList

app_name = 'shop_type'

urlpatterns = [
    url(r'^$', login_required(ShopTypeList.as_view(), login_url='authentications:login'), name="shop_type_list"),
    url(r'^create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="shop_type_create"),
    url(r'^(?P<shop_type_id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="shop_type_edit"),
    url(r'^(?P<id>[0-9A-Za-z]+)/detail/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="shop_type_detail"),
    url(r'^(?P<id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'), name="shop_type_delete"),
]
