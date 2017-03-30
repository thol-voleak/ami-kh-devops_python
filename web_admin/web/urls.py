from django.conf.urls import url
from . import views

app_name = 'web'

urlpatterns = [
    url(r'^$', views.index, name="web-index"),
    url(r'^backlog$', views.backlog, name="backlog"),
]
