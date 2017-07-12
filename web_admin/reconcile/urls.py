from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.partner_report import PartnerReport
from .views.sof_report import SofReport
from .views.partner_file_list import PartnerFileList
from .views.sof_file_list import SofFileList
from .views.service_list import ServiceList

app_name = 'reconcile'

urlpatterns = [
    url(r'^partner/file-list/$', login_required(PartnerFileList.as_view(),
                                                login_url='authentications:login'), name="reconcile_partner_file_list"),
    url(r'^partner/report/$', login_required(PartnerReport.as_view(),
                                                login_url='authentications:login'), name="reconcile_partner_report"),
    url(r'^partner/report/(?P<partner_file_id>[0-9A-Za-z]+)/$', login_required(PartnerReport.as_view(),
                                                login_url='authentications:login'), name="reconcile_partner_report_by_file_id"),
    url(r'^sof/file-list/$', login_required(SofFileList.as_view(),
                                                login_url='authentications:login'), name="reconcile_sof_file_list"),
    url(r'^sof/report/$', login_required(SofReport.as_view(),
                                                login_url='authentications:login'), name="reconcile_sof_report"),
    url(r'^sof/report/(?P<sofFileId>[0-9A-Za-z]+)/$', login_required(SofReport.as_view(),
                                                login_url='authentications:login'), name="reconcile_sof_report_by_file_id"),
    url(r'^service/list/$', login_required(ServiceList.as_view(),
                                         login_url='authentications:login'), name="reconcile_service_list")
]
