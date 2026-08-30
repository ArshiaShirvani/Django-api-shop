from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("",views.HomeAPIView.as_view(),name="index"),
    path("contact",views.ContactMessageAPIView.as_view(),name="contact"),
]