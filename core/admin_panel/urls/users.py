from django.urls import path

from ..views.users import (
    AdminUserListAPIView,
    AdminUserDetailAPIView,
    AdminUserStatusAPIView,
)


urlpatterns = [

    path(
        "",
        AdminUserListAPIView.as_view(),
        name="users",
    ),

    path(
        "<int:pk>/",
        AdminUserDetailAPIView.as_view(),
        name="user-detail",
    ),

    path(
        "<int:pk>/status/",
        AdminUserStatusAPIView.as_view(),
        name="user-status",
    ),

]