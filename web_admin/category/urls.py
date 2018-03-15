from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from .views.add_category import AddCategory
from .views.edit_category import EditCategory
from .views.delete_category import delete
from .views.list import CategoryList
from .views.update_product_status import UpdateProductStatusOfCategory
from .views.category_data import CategoryData

app_name = 'category'

urlpatterns = [
    url(r'^$', login_required(CategoryList.as_view(), login_url='authentications:login'), name="categories"),
    url(r'^create$', login_required(AddCategory.as_view(), login_url='authentications:login'), name="category_add"),
    url(r'^update/(?P<categoryId>[0-9A-Za-z]+)/$', login_required(EditCategory.as_view(), login_url='authentications:login'), name="category_edit"),
    url(r'^product/(?P<categoryId>[0-9A-Za-z]+)/status/update$',
        login_required(UpdateProductStatusOfCategory.as_view(), login_url='authentications:login'), name="update_product_status_in_category"),
    url(r'^delete/(?P<categoryId>[0-9A-Za-z]+)/$', login_required(delete, login_url='authentications:login'), name="category_delete"),
    url(r'^get_category_data/(?P<categoryId>[0-9A-Za-z]+)/$', login_required(CategoryData.as_view(), login_url='authentications:login'), name="get_category_data"),
]
