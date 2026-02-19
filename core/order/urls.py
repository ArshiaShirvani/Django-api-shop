from django.urls import path
from . import views


app_name = "order"


urlpatterns = [
    path("create/", views.OrderCreateApiView.as_view(), name="order-create"),
    path("<int:pk>/", views.OrderDetailApiView.as_view(), name="order-detail"),
    path("list/", views.UserOrdersListApiView.as_view(), name="user-orders"),
]