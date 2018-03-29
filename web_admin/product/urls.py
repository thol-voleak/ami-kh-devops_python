from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from product.views.product.create import CreateView
from .views.product.list import ListView
from product.views.product.edit import EditView
from product.views.product.detail import ProductDetail
from product.views.product.delete import ProductDelete

app_name = 'product'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="products"),
    url(r'^create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="product_create"),
    url(r'^(?P<product_id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="product_edit"),
    url(r'^(?P<product_id>[0-9A-Za-z]+)/detail/$', login_required(ProductDetail.as_view(), login_url='authentications:login'), name="product_detail"),
    url(r'^delete/$', login_required(ProductDelete.as_view(), login_url='authentications:login'), name="product_delete"),
]
