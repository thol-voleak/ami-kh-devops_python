from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from .views.partner_file_list import PartnerFileList
from .views.sof_file_list import SofFileList

app_name = 'reconcile'

urlpatterns = [
    url(r'^partner/file-list/$', login_required(PartnerFileList.as_view(),
                                                login_url='authentications:login'), name="reconcile_partner_file_list"),
    url(r'^partner/report/$', login_required(PartnerFileList.as_view(),
                                                login_url='authentications:login'), name="reconcile_partner_report"),
    url(r'^sof/file-list/$', login_required(SofFileList.as_view(),
                                                login_url='authentications:login'), name="reconcile_sof_file_list"),
    url(r'^sof/report/$', login_required(PartnerFileList.as_view(),
                                                login_url='authentications:login'), name="reconcile_partner_report"),
]
