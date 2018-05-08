from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView

app_name = 'password_center'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='authentications:login'), name="list"),
]
