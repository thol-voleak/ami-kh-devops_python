from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.country_code import CountryCode

app_name = 'configuration'

urlpatterns = [
    url(r'^country-code/$', login_required(CountryCode.as_view(), login_url='login'), name="country-code"),
]
