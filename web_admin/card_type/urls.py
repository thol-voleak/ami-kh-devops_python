from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ListView

app_name = 'card_type'

urlpatterns = [
    url(r'^list$', login_required(ListView.as_view(), login_url='authentications:login'), name="card-type-list"),
]