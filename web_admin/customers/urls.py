from .views.list import ListView
from .views.customer_detail import CustomerDetailView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

app_name = 'customers'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'), name="customer-list"),
    url(r'^(?P<customerId>[0-9A-Za-z]+)/$', login_required(CustomerDetailView.as_view(), login_url='login'), name="customer_detail"),
]
