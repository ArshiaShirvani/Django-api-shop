from . import views
from django.urls import path

app_name = "shop"

urlpatterns = [
    path("test/", views.TestApiView.as_view(), name="test"),
]