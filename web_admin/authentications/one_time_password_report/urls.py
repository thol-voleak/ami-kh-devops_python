from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.list import OTPList

app_name = 'one_time_password_report'

urlpatterns = [
    url(r'^list$', login_required(OTPList.as_view(), login_url='authentications:login'),
        name="list"),
]
