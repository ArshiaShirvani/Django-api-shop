from django.urls import path

from admin_panel.views.shipping_methods import (
    AdminShippingMethodListAPIView,
    AdminShippingMethodCreateAPIView,
    AdminShippingMethodDetailAPIView,
    AdminShippingMethodUpdateAPIView,
    AdminShippingMethodDeleteAPIView,
)


urlpatterns = [
    path(
        "",
        AdminShippingMethodListAPIView.as_view(),
        name="shipping-method-list",
    ),

    path(
        "create/",
        AdminShippingMethodCreateAPIView.as_view(),
        name="shipping-method-create",
    ),

    path(
        "<int:pk>/",
        AdminShippingMethodDetailAPIView.as_view(),
        name="shipping-method-detail",
    ),

    path(
        "<int:pk>/update/",
        AdminShippingMethodUpdateAPIView.as_view(),
        name="shipping-method-update",
    ),

    path(
        "<int:pk>/delete/",
        AdminShippingMethodDeleteAPIView.as_view(),
        name="shipping-method-delete",
    ),
]