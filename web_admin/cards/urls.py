from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.profile import ProfileView
from .views.history import HistoryView
from .views.card_freeze_list import CardFreezeList

app_name = 'cards'

urlpatterns = [
    url(r'^profile/$', login_required(ProfileView.as_view(), login_url='authentications:login'), name="profile"),
    url(r'^history/$', login_required(HistoryView.as_view(), login_url='authentications:login'), name="history"),
    url(r'^card-freeze-list/$', login_required(CardFreezeList.as_view(), login_url='authentications:login'),
        name="card_freeze_list"),
    url(r'^card-freeze-list/delete/(?P<id>[^/]+)/$', login_required(CardFreezeList.as_view(), login_url='authentications:login'),
        name="delete_card_freeze"),

]
