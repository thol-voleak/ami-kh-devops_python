from django.conf.urls import url

from . import views

app_name = 'client_credentials'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]