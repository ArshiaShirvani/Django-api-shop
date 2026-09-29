from django.urls import path

from admin_panel.views.reviews import (
    AdminReviewListAPIView,
    AdminReviewCreateAPIView,
    AdminReviewDetailAPIView,
    AdminReviewUpdateAPIView,
    AdminReviewDeleteAPIView,
)


urlpatterns = [
    path(
        "",
        AdminReviewListAPIView.as_view(),
        name="review-list",
    ),

    path(
        "create/",
        AdminReviewCreateAPIView.as_view(),
        name="review-create",
    ),

    path(
        "<int:pk>/",
        AdminReviewDetailAPIView.as_view(),
        name="review-detail",
    ),

    path(
        "<int:pk>/update/",
        AdminReviewUpdateAPIView.as_view(),
        name="review-update",
    ),

    path(
        "<int:pk>/delete/",
        AdminReviewDeleteAPIView.as_view(),
        name="review-delete",
    ),
]