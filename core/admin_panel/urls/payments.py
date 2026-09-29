from django.urls import path

from admin_panel.views.payments import (
    AdminPaymentListAPIView,
    AdminPaymentDetailAPIView,
)


urlpatterns = [

    path(
        "",
        AdminPaymentListAPIView.as_view(),
        name="payment-list",
    ),

    path(
        "<int:pk>/",
        AdminPaymentDetailAPIView.as_view(),
        name="payment-detail",
    ),

]