from django.urls import path

from . import views


app_name = "order"


urlpatterns = [

    # =====================================================
    # Addresses
    # =====================================================

    path(
        "addresses/",
        views.AddressListCreateAPIView.as_view(),
        name="address-list-create",
    ),

    path(
        "addresses/<int:pk>/",
        views.AddressDetailAPIView.as_view(),
        name="address-detail",
    ),

    # =====================================================
    # Shipping Methods
    # =====================================================

    path(
        "shipping-methods/",
        views.ShippingMethodListAPIView.as_view(),
        name="shipping-method-list",
    ),

    # =====================================================
    # Coupon
    # =====================================================

    path(
        "coupon/validate/",
        views.CouponApplyAPIView.as_view(),
        name="coupon-validate",
    ),

    # =====================================================
    # Create Order
    # =====================================================

    path(
        "create/",
        views.OrderCreateAPIView.as_view(),
        name="order-create",
    ),

    # =====================================================
    # My Orders
    # =====================================================

    path(
        "",
        views.MyOrdersAPIView.as_view(),
        name="order-list",
    ),

    # =====================================================
    # Order Detail
    # =====================================================

    path(
        "<str:order_number>/",
        views.OrderDetailAPIView.as_view(),
        name="order-detail",
    ),

    # =====================================================
    # Cancel Order
    # =====================================================

    path(
        "<str:order_number>/cancel/",
        views.OrderCancelAPIView.as_view(),
        name="order-cancel",
    ),
]