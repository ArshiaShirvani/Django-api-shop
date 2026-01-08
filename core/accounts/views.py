from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView


from django.utils import timezone
from datetime import timedelta
import random

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RequestOtpSerializer, VerifyOtpSerializer,LogoutSerializer
from .models import User, OTP



class RequestOtpView(GenericAPIView):
    serializer_class = RequestOtpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        user, created = User.objects.get_or_create(phone_number=phone_number)

        code = str(random.randint(1000, 9999))

        OTP.objects.create(
            phone_number=phone_number,
            code=code,
            expires_date=timezone.now() + timedelta(minutes=2)
        )

        return Response(
            {"message": "کد با موفقیت ارسال شد",
             "code":code},
            status=status.HTTP_200_OK
        )


        

class VerifyOtpView(GenericAPIView):
    serializer_class = VerifyOtpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({"error": "کاربری یافت نشد"}, status=404)

        otp = OTP.objects.filter(
            phone_number=phone_number,
            code=code,
            is_used=False
        ).first()

        if not otp:
            return Response({"error": "کد نامعتبر است"}, status=400)

        if otp.expires_date < timezone.now():
            return Response({"error": "کد منقضی شده است"}, status=400)

        otp.is_used = True
        otp.save()

        user.is_active = True
        user.is_verified = True
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "ورود با موفقیت انجام شد",
            "role":user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })




class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"error": "توکن نامعتبر است"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "با موفقیت از حساب کاربری خارج شدید"},
            status=status.HTTP_200_OK
        )
