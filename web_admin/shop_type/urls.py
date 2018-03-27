from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ShopTypeList

app_name = 'shop_type'

urlpatterns = [
    url(r'^$', login_required(ShopTypeList.as_view(), login_url='authentications:login'), name="shop_type_list"),
]
