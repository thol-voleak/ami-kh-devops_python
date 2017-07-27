from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from card_type.views.detail import CardTypeDetail
from .views.list import ListView
from .views.update import CardTypeUpdateForm

app_name = 'card_type'

urlpatterns = [
    url(r'^list$', login_required(ListView.as_view(), login_url='authentications:login'), name="card-type-list"),
    url(r'^detail/(?P<card_type_id>[0-9A-Za-z]+)/$',
        login_required(CardTypeDetail.as_view(), login_url='authentications:login'), name="card_type_detail"),
    url(r'^update/(?P<cardTypeId>[0-9A-Za-z]+)/$',
        login_required(CardTypeUpdateForm.as_view(), login_url='authentications:login'), name="card-type-update"),
]