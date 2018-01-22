from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.list import ReportConfigurationList

app_name = 'report_configuration'

urlpatterns = [
    url(r'^$', login_required(ReportConfigurationList.as_view(),
                                                login_url='authentications:login'), name="report_configuration"),
]
