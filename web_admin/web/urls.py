from django.conf.urls import url
from . import views

app_name = 'web'

urlpatterns = [
    url(r'^$', views.index, name="web-index"),
    url(r'^permission-denied', views.permission_denied, name="permission_denied"),
    url(r'^backlog$', views.backlog, name="backlog"),
]
