from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import VoucherList
from .views.detail import VoucherDetail
from.views.transit import Transit


app_name = 'voucher'

urlpatterns = [
    url(r'^$', login_required(VoucherList.as_view(), login_url='authentications:login'), name="voucher"),
    url(r'^detail/(?P<voucher_id>[0-9A-Za-z]+)/$', login_required(VoucherDetail.as_view(), login_url='authentications:login'), name="voucher_detail"),
    url(r'^create/$', login_required(Transit.as_view(), login_url='authentications:login'), name="create_new_voucher"),
]