from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.payment_order_list import PaymentOrderView

app_name = 'payments'

urlpatterns = [
    url(r'^orders/$', login_required(PaymentOrderView.as_view(), login_url='authentications:login'), name="payment_order"),
]
