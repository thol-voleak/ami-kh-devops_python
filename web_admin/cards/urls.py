from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.profile import ProfileView
from .views.history import HistoryView

app_name = 'cards'

urlpatterns = [
    url(r'^profile/$', login_required(ProfileView.as_view(), login_url='login'), name="profile"),
    url(r'^history/$', login_required(HistoryView.as_view(), login_url='login'), name="history"),
]
