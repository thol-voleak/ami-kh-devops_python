from django.conf.urls import url

from . import views

app_name = 'authentications'

urlpatterns = [
    url(r'^$', views.form, name='form'),
    url(r'^login$', views.login, name='login'),
    url(r'^welcome$', views.welcome, name='welcome'),
]