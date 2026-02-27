from . import views
from django.urls import path,re_path

app_name = "shop"

urlpatterns = [
    path("products",views.ProductListApiView.as_view(),name="product-list"),
    re_path(r"^products/(?P<slug>.+)/$", views.ProductDetailApiView.as_view(), name="product-detail"),
    # path("detail/<slug:slug>/",views.ProductDetailApiView.as_view(),name="product-detail"),
    # path('categories/', CategoryListAPI.as_view()),
    # path('categories/<slug:slug>/', CategoryDetailAPI.as_view()),
]