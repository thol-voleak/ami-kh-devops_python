from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views.list import CardDesignList
from .views.create import CreateView
from .views.detail import DetailView
from .views.update import UpdateView


app_name = 'card_design'

urlpatterns = [
    url(r'^$', login_required(CardDesignList.as_view(), login_url='authentications:login'), name="card_designs"),
    url(r'^add/$', login_required(CreateView.as_view(), login_url='authentications:login'), name="create_card_design"),
    url(r'^providers/(?P<provider_id>[0-9A-Za-z]+)/details/(?P<card_id>[0-9A-Za-z]+)/$', login_required(DetailView.as_view(), login_url='authentications:login'), name="card_design_detail"),
    url(r'^providers/(?P<provider_id>[0-9A-Za-z]+)/update/(?P<card_id>[0-9A-Za-z]+)/$', login_required(UpdateView.as_view(), login_url='authentications:login'), name="card_design_update"),
]

