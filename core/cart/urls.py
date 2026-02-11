from django.urls import path
from . import views


app_name = "cart"


urlpatterns = [
    path("", views.CartDetailAPIView.as_view(), name="cart-detail"),
    path("items/", views.CartAddItemAPIView.as_view(), name="cart-add-item"),
    path("items/<int:pk>/", views.CartItemUpdateAPIView.as_view(), name="cart-update-item"),
    path("items/<int:pk>/delete/", views.CartItemDeleteAPIView.as_view(), name="cart-delete-item"),
]
