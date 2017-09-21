from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import CardProviderList
from .views.update import UpdateView
from .views.detail import DetailView
from .views.create import CardProviderCreate


app_name = 'card_provider'

urlpatterns = [
    url(r'^$', login_required(CardProviderList.as_view(), login_url='authentications:login'), name="card_provider"),
    url(r'^update/(?P<provider_id>[0-9A-Za-z]+)/$', login_required(UpdateView.as_view(), login_url='authentications:login'), name="update_card_provider"),
    url(r'^detail/(?P<provider_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="detail_card_provider"),
    url(r'^create/$', login_required(CardProviderCreate.as_view(), login_url='authentications:login'), name="create"),
]
