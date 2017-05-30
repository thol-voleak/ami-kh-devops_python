from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import BankSofsListView

app_name = 'bank_sofs'

urlpatterns = [
    url(r'^bank/$', login_required(BankSofsListView.as_view(), login_url='login'), name="bank_list"),
]
