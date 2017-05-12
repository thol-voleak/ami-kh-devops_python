from centralize_configuration.views import ScopeListView, ConfigurationListView

from django.contrib.auth.decorators import login_required
from django.conf.urls import url

app_name = 'centralize_configuration'

urlpatterns = [
    url(r'^scopes/list$', login_required(ScopeListView.as_view(), login_url='login'), name="scope_list"),
    url(r'^scopes/(?P<scope>[^/]+)/configurations/list$', login_required(ConfigurationListView.as_view(), login_url='login'),
        name="configuration_list")
]
