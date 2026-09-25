from django.urls import path

from ..views.dashboard import (
    AdminDashboardOverviewAPIView,
)


urlpatterns = [

    path(
        "",
        AdminDashboardOverviewAPIView.as_view(),
        name="dashboard",
    ),

]