from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from trust_management.views.list import TrustList

app_name = 'trust_management'

urlpatterns = [
    url(r'^$', login_required(TrustList.as_view(), login_url='authentications:login'), name="trust_list"),
    # url(r'^$', login_required(ShopTypeList.as_view(), login_url='authentications:login'), name="shop_type_list"),
    # url(r'^create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="shop_type_create"),
    # url(r'^(?P<shop_type_id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="shop_type_edit"),
    # url(r'^(?P<id>[0-9A-Za-z]+)/detail/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="shop_type_detail"),
    # url(r'^(?P<id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'), name="shop_type_delete"),
]
