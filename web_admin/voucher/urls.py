from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import VoucherList


app_name = 'voucher'

urlpatterns = [
    url(r'^$', login_required(VoucherList.as_view(), login_url='authentications:login'), name="voucher"),
]