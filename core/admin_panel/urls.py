from django.urls import include, path


urlpatterns = [

    path(
        "dashboard/",
        include("admin_panel.urls.dashboard"),
    ),

    path(
        "users/",
        include("admin_panel.urls.users"),
    ),

    path(
        "products/",
        include("admin_panel.urls.products"),
    ),

]