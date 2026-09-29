from django.urls import path

from admin_panel.views.coupons import (
    AdminCouponListAPIView,
    AdminCouponCreateAPIView,
    AdminCouponDetailAPIView,
    AdminCouponUpdateAPIView,
    AdminCouponDeleteAPIView,
    AdminCouponUsageListAPIView,
    AdminCouponUsageDetailAPIView,
)


urlpatterns = [

    # =====================================================
    # COUPONS
    # =====================================================

    path(
        "",
        AdminCouponListAPIView.as_view(),
        name="coupon-list",
    ),

    path(
        "create/",
        AdminCouponCreateAPIView.as_view(),
        name="coupon-create",
    ),

    path(
        "<int:pk>/",
        AdminCouponDetailAPIView.as_view(),
        name="coupon-detail",
    ),

    path(
        "<int:pk>/update/",
        AdminCouponUpdateAPIView.as_view(),
        name="coupon-update",
    ),

    path(
        "<int:pk>/delete/",
        AdminCouponDeleteAPIView.as_view(),
        name="coupon-delete",
    ),

    # =====================================================
    # COUPON USAGE
    # =====================================================

    path(
        "usage/",
        AdminCouponUsageListAPIView.as_view(),
        name="coupon-usage-list",
    ),

    path(
        "usage/<int:pk>/",
        AdminCouponUsageDetailAPIView.as_view(),
        name="coupon-usage-detail",
    ),
]