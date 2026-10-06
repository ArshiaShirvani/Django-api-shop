from django.urls import include, path


urlpatterns = [
    path("dashboard/", include("admin_panel.urls.dashboard")),
    path("users/", include("admin_panel.urls.users")),
    path("products/", include("admin_panel.urls.products")),
    path("orders/", include("admin_panel.urls.orders")),
    path("payments/", include("admin_panel.urls.payments")),
    path("coupons/", include("admin_panel.urls.coupons")),
    path("shipping-methods/", include("admin_panel.urls.shipping_methods")),
    path("reviews/", include("admin_panel.urls.reviews")),
    path("website/", include("admin_panel.urls.website")),
    path("tickets/", include("admin_panel.urls.tickets")),
    
]