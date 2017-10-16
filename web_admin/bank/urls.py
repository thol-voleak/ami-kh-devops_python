from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from bank.views.bank.create import CreateView
from bank.views.bank.delete import DeleteView
from bank.views.bank.edit import EditView
from bank.views.bank.list import ListView
from bank.views.bank.detail import DetailsView


app_name = 'bank'

urlpatterns = [
    url(r'^management/$', login_required(ListView.as_view(), login_url='authentications:login'), name="bank_sofs_list"),
    url(r'^sofs/create/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="bank_sofs_create"),
    url(r'^sofs/(?P<bank_id>[0-9A-Za-z]+)/edit/$', login_required(EditView.as_view(), login_url='authentications:login'), name="bank_sofs_edit"),
    url(r'^sofs/(?P<bank_id>[0-9A-Za-z]+)/detail/$', login_required(DetailsView.as_view(), login_url='authentications:login'), name="bank_sofs_detail"),
    url(r'^sofs/(?P<bank_id>[0-9A-Za-z]+)/delete/$', login_required(DeleteView.as_view(), login_url='authentications:login'), name="bank_sofs_delete"),
]