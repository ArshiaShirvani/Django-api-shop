from django.urls import path

from .views import (
    ReviewListCreateView,
    ReviewUpdateView,
    ReviewDeleteAPIView,
)

app_name = "review"

urlpatterns = [
    path(
        "product/<int:product_id>/",
        ReviewListCreateView.as_view(),
        name="product-reviews",
    ),

    path(
        "<int:pk>/update/",
        ReviewUpdateView.as_view(),
        name="review-update",
    ),
    path(
        "<int:pk>/delete/",
        ReviewDeleteAPIView.as_view(),
        name="review-delete"
    ),
]