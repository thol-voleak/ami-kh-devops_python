from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.create import FPCreateView


app_name = 'fraud_prevention'

urlpatterns = [
    url(r'^$', login_required(FPCreateView.as_view(), login_url='authentications:login'), name="fraud_prevention"),
]
