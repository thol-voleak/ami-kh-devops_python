from .views.list import ListView
from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'agents'

urlpatterns = [
    url(r'^$', login_required(ListView.as_view(), login_url='login'),
        name="agent-list"),
]
