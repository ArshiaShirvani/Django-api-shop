from django.urls import path

from .views import (
    DashboardProfileAPIView,

    DashboardOrderListAPIView,
    DashboardOrderDetailAPIView,

    DashboardAddressListCreateAPIView,
    DashboardAddressDetailAPIView,

    DashboardFavoriteListCreateAPIView,
    DashboardFavoriteDeleteAPIView,
)


app_name = "dashboard"


urlpatterns = [

    # =====================================================
    # PROFILE
    # =====================================================

    path(
        "profile/",
        DashboardProfileAPIView.as_view(),
        name="profile",
    ),


    # =====================================================
    # ORDERS
    # =====================================================

    path(
        "orders/",
        DashboardOrderListAPIView.as_view(),
        name="order-list",
    ),

    path(
        "orders/<int:pk>/",
        DashboardOrderDetailAPIView.as_view(),
        name="order-detail",
    ),


    # =====================================================
    # ADDRESSES
    # =====================================================

    path(
        "addresses/",
        DashboardAddressListCreateAPIView.as_view(),
        name="address-list-create",
    ),

    path(
        "addresses/<int:pk>/",
        DashboardAddressDetailAPIView.as_view(),
        name="address-detail",
    ),


    # =====================================================
    # FAVORITES
    # =====================================================

    path(
        "favorites/",
        DashboardFavoriteListCreateAPIView.as_view(),
        name="favorite-list-create",
    ),

    path(
        "favorites/<int:product_id>/",
        DashboardFavoriteDeleteAPIView.as_view(),
        name="favorite-delete",
    ),
]