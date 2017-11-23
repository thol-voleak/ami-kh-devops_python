from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.profile import ProfileView
from .views.history import HistoryView
from .views.card_freeze_list import CardFreezeList
from .views.active import active
from .views.deactive import deactive

app_name = 'cards'

urlpatterns = [
    url(r'^profile/$', login_required(ProfileView.as_view(), login_url='authentications:login'), name="profile"),
    url(r'^history/$', login_required(HistoryView.as_view(), login_url='authentications:login'), name="history"),
    url(r'^card-freeze-list/$', login_required(CardFreezeList.as_view(), login_url='authentications:login'),
        name="card_freeze_list"),
    url(r'^card-freeze-list/delete/(?P<id>[^/]+)/$', login_required(CardFreezeList.as_view(), login_url='authentications:login'),
        name="delete_card_freeze"),
    url(r'^profile-card/(?P<id>[0-9A-Za-z]+)/activate/$', login_required(active, login_url='authentications:login'),
        name="activate_profile_card"),
    url(r'^profile-card/(?P<id>[0-9A-Za-z]+)/deactivate/$', login_required(deactive, login_url='authentications:login'),
        name="deactivate_profile_card"),
]
