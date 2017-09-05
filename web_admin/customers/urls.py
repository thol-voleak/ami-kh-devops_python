from .views.list import ListView
from .views.customer_detail import CustomerDetailView
from .views.update import UpdateView
from .views.customer_sof_list import CustomerSOFListView
from .views.customer_identities import CustomerIdentitiesListView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.suspend import suspend
from .views.activate import activate
from .views.reset_identity_password import reset_password

app_name = 'customers'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="customer-list"),
    url(r'^(?P<customerId>[0-9A-Za-z]+)/$', login_required(CustomerDetailView.as_view(), login_url='authentications:login'), name="customer_detail"),
    url(r'^(?P<customerId>[0-9A-Za-z]+)/update/$', login_required(UpdateView.as_view(), login_url='authentications:login'), name="customer_update"),
    url(r'^(?P<customerId>[0-9A-Za-z]+)/sofs/bank/$', login_required(CustomerSOFListView.as_view(), login_url='authentications:login'), name="customer_sof_list"),
    url(r'^(?P<customerId>[0-9A-Za-z]+)/identities/$', login_required(CustomerIdentitiesListView.as_view(), login_url='authentications:login'), name="customer_identities"),
    url(r'^suspend/(?P<customer_id>[0-9A-Za-z]+)/$', login_required(suspend, login_url='authentications:login'),
        name="suspend-customer"),
    url(r'^activate/(?P<customer_id>[0-9A-Za-z]+)/$', login_required(activate, login_url='authentications:login'),
        name="activate-customer"),
    url(r'^(?P<customer_id>[0-9A-Za-z]+)/identities/(?P<identity_id>[0-9A-Za-z]+)/$', login_required(reset_password, login_url='authentications:login'), name="reset-identity-password"),
]
