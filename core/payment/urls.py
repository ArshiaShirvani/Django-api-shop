from django.urls import path

from .views import (
    PaymentCreateAPIView,
    PaymentCallbackAPIView,
)


app_name = "payment"


urlpatterns = [

    path(
        "create/",
        PaymentCreateAPIView.as_view(),
        name="payment-create",
    ),

    path(
        "callback/",
        PaymentCallbackAPIView.as_view(),
        name="payment-callback",
    ),

]