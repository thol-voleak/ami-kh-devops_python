from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.add_category import AddCategory
from .views.edit_category import EditCategory
from .views.list import CategoryList
from .views.update_product_status import UpdateProductStatusOfCategory

app_name = 'category'

urlpatterns = [
    url(r'^$', login_required(CategoryList.as_view(), login_url='authentications:login'), name="categories"),
    url(r'^create$', login_required(AddCategory.as_view(), login_url='authentications:login'), name="category_add"),
    url(r'^update/(?P<categoryId>[0-9A-Za-z]+)/$', login_required(EditCategory.as_view(), login_url='authentications:login'), name="category_edit"),
    url(r'^product/(?P<categoryId>[0-9A-Za-z]+)/status/update$',
        login_required(UpdateProductStatusOfCategory.as_view(), login_url='authentications:login'), name="update_product_status_in_category"),

]
