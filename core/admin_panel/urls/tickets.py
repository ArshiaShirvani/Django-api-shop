from django.urls import path

from admin_panel.views.tickets import (
    AdminTicketListView,
    AdminTicketDetailView,
)


urlpatterns = [

    # =====================================================
    # TICKETS
    # =====================================================

    path(
        "",
        AdminTicketListView.as_view(),
        name="admin-tickets",
    ),

    path(
        "<int:pk>/",
        AdminTicketDetailView.as_view(),
        name="admin-ticket-detail",
    ),
]