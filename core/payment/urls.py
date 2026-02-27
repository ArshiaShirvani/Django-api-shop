from django.urls import path
from .views import PaymentRequestApiView, PaymentVerifyApiView

app_name = "payment"

urlpatterns = [
    path("request/<int:order_id>/", PaymentRequestApiView.as_view(), name="request"),
    path("verify/", PaymentVerifyApiView.as_view(), name="verify"),
]