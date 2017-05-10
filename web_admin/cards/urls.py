from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView

app_name = 'cards'

urlpatterns = [
    url(r'^profile/$', login_required(ListView.as_view(), login_url='login'), name="profile"),
]
