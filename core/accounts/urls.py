from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth', views.RequestOtpView.as_view(), name='otp-request'),
    path('auth/verify/', views.VerifyOtpView.as_view(), name='otp-verify'),
    path("token/refresh/",TokenRefreshView.as_view(),name="refresh-token"),
    path('information', views.CurrentUserApiView.as_view(), name='information'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]