from bank_sofs.views.list import ListView
from bank_sofs.views.create import CreateView
from bank_sofs.views.edit import UpdateView
from bank_sofs.views.detail import DetailsView
from bank_sofs.views.delete import DeleteView

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'bank_sofs'

urlpatterns = [
    url(r'^bank/$', login_required(ListView.as_view(), login_url='login'), name="bank_sofs_list"),
    url(r'^bank/create$', login_required(CreateView.as_view(), login_url='login'), name="bank_sofs_create"),
    url(r'^bank/(?P<bank_id>[0-9A-Za-z]+)/edit$', login_required(UpdateView.as_view(), login_url='login'), name="bank_sofs_edit"),
    url(r'^bank/(?P<bank_id>[0-9A-Za-z]+)/detail$', login_required(DetailsView.as_view(), login_url='login'), name="bank_sofs_detail"),
    url(r'^bank/(?P<bank_id>[0-9A-Za-z]+)/delete$', login_required(DeleteView.as_view(), login_url='login'), name="bank_sofs_delete"),
]
