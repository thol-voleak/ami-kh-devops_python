from card_sofs.views.card_sof_list import CardSOFView

from django.conf.urls import url
from django.contrib.auth.decorators import login_required


app_name = 'card_sofs'

urlpatterns = [
    url(r'^sofs/$', login_required(CardSOFView.as_view(), login_url='authentications:login'), name="card_sof")
]
