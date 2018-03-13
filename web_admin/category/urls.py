from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.add_category import AddCategory
from .views.list import CategoryList

app_name = 'category'

urlpatterns = [
    url(r'^categories/$', login_required(CategoryList.as_view(), login_url='authentications:login'), name="categories"),
    url(r'^create$', login_required(AddCategory.as_view(), login_url='authentications:login'), name="category_add"),
]
