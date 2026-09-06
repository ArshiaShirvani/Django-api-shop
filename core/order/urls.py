from django.urls import path

from .views import (
    AddressListCreateAPIView,
    AddressDetailAPIView,
    ShippingMethodListAPIView,
    CouponApplyAPIView,
    OrderCreateAPIView,
    MyOrderListAPIView,
    MyOrderDetailAPIView,
)


app_name = "order"


urlpatterns = [

    # =====================================================
    # ADDRESSES
    # =====================================================

    path(
        "addresses/",
        AddressListCreateAPIView.as_view(),
        name="address-list-create",
    ),

    path(
        "addresses/<int:pk>/",
        AddressDetailAPIView.as_view(),
        name="address-detail",
    ),


    # =====================================================
    # SHIPPING METHODS
    # =====================================================

    path(
        "shipping-methods/",
        ShippingMethodListAPIView.as_view(),
        name="shipping-method-list",
    ),


    # =====================================================
    # COUPON
    # =====================================================

    path(
        "apply-coupon/",
        CouponApplyAPIView.as_view(),
        name="apply-coupon",
    ),


    # =====================================================
    # CREATE ORDER
    # =====================================================

    path(
        "create/",
        OrderCreateAPIView.as_view(),
        name="order-create",
    ),


    # =====================================================
    # MY ORDERS
    # =====================================================

    path(
        "my-orders/",
        MyOrderListAPIView.as_view(),
        name="my-order-list",
    ),

    path(
        "my-orders/<int:pk>/",
        MyOrderDetailAPIView.as_view(),
        name="my-order-detail",
    ),
]