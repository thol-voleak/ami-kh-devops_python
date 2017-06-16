from .views.list import ListView
from .views.customer_detail import CustomerDetailView
from .views.customer_sof_list import CustomerSOFListView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

app_name = 'customers'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="customer-list"),
    url(r'^(?P<customerId>[0-9A-Za-z]+)/$', login_required(CustomerDetailView.as_view(), login_url='authentications:login'), name="customer_detail"),
    url(r'^(?P<customerId>[0-9A-Za-z]+)/sofs/bank/$', login_required(CustomerSOFListView.as_view(), login_url='authentications:login'), name="customer_sof_list"),

]
