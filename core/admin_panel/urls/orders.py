from django.urls import path

from admin_panel.views.orders import (
    AdminOrderListAPIView,
    AdminOrderDetailAPIView,
    AdminOrderStatusUpdateAPIView,
)


urlpatterns = [

    # =====================================================
    # ORDER LIST
    # =====================================================

    path(
        "",
        AdminOrderListAPIView.as_view(),
        name="order-list",
    ),

    # =====================================================
    # ORDER DETAIL
    # =====================================================

    path(
        "<int:pk>/",
        AdminOrderDetailAPIView.as_view(),
        name="order-detail",
    ),

    # =====================================================
    # ORDER STATUS
    # =====================================================

    path(
        "<int:pk>/status/",
        AdminOrderStatusUpdateAPIView.as_view(),
        name="order-status-update",
    ),

]