from . import views
from django.urls import path

app_name = "shop"

urlpatterns = [
    path("test/", views.TestApiView.as_view(), name="test"),
    path("products/",views.ProductListApiView.as_view(),name="product-list"),
    path("products/<slug:slug>/", views.ProductDetailApiView.as_view(),name="product-detail"),
    # path("detail/<slug:slug>/",views.ProductDetailApiView.as_view(),name="product-detail"),
    # path('categories/', CategoryListAPI.as_view()),
    # path('categories/<slug:slug>/', CategoryDetailAPI.as_view()),
]