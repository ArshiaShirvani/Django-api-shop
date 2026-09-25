from django.urls import path

from ..views.products import *


urlpatterns = [
    # Products
    path("", AdminProductListAPIView.as_view(), name="products"),
    path("create/", AdminProductCreateAPIView.as_view(), name="product-create"),
    path("<int:pk>/", AdminProductDetailAPIView.as_view(), name="product-detail"),
    path("<int:pk>/status/", AdminProductStatusAPIView.as_view(), name="product-status"),

    # Product Options
    path("options/", AdminProductOptionsAPIView.as_view(), name="product-options"),

    # Create Options
    path(
        "categories/create/",
        AdminProductCategoryCreateAPIView.as_view(),
        name="product-category-create",
    ),
    path(
        "sizes/create/",
        AdminProductSizeCreateAPIView.as_view(),
        name="product-size-create",
    ),
    path(
        "colors/create/",
        AdminProductColorCreateAPIView.as_view(),
        name="product-color-create",
    ),
    path(
        "features/create/",
        AdminProductFeatureCreateAPIView.as_view(),
        name="product-feature-create",
    ),

    # Images
    path(
        "<int:pk>/images/",
        AdminProductImageUploadAPIView.as_view(),
        name="product-image-upload",
    ),
    path(
        "<int:pk>/images/<int:image_id>/",
        AdminProductImageDeleteAPIView.as_view(),
        name="product-image-delete",
    ),
    path(
        "<int:pk>/images/<int:image_id>/main/",
        AdminProductImageMainAPIView.as_view(),
        name="product-image-main",
    ),
    path(
        "categories/<int:pk>/",
        AdminProductCategoryUpdateAPIView.as_view(),
        name="product-category-update",
    ),

    path(
        "sizes/<int:pk>/",
        AdminProductSizeUpdateAPIView.as_view(),
        name="product-size-update",
    ),

    path(
        "colors/<int:pk>/",
        AdminProductColorUpdateAPIView.as_view(),
        name="product-color-update",
    ),

    path(
        "features/<int:pk>/",
        AdminProductFeatureUpdateAPIView.as_view(),
        name="product-feature-update",
    ),

]