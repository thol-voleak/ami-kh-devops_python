from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.add_category import AddCategory

app_name = 'category'

urlpatterns = [
    url(r'^add$', login_required(AddCategory.as_view(), login_url='authentications:login'), name="category_add"),
]
