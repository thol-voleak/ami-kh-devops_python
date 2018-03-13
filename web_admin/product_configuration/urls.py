from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'product_configuration'

urlpatterns = [
    # url(r'^/$', login_required(PaymentOrderView.as_view(), login_url='authentications:login'), name="product_configuration"),
]
