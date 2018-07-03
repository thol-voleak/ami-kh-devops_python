from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.payment_order_list import PaymentOrderView
from .views.order_detail import OrderDetailView
from .views.user_list import UserList

app_name = 'payments'

urlpatterns = [
    url(r'^orders/$', login_required(PaymentOrderView.as_view(), login_url='authentications:login'), name="payment_order"),
    url(r'^orders/(?P<order_id>[0-9A-Za-z]+)/details$', login_required(OrderDetailView.as_view(), login_url='authentications:login'), name="order_detail"),
    url(r'^users/$', login_required(UserList.as_view(), login_url='authentications:login'),
        name="search_user")

]
