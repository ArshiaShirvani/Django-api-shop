from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from accounts.models import User
from shop.models import Product
from order.models import Order
from payment.models import Payment, PaymentStatus

from ..permissions import IsAdminPanelUser

from ..serializers.dashboard import (
    AdminOverviewSerializer,
)


# =========================================================
# DASHBOARD OVERVIEW
# =========================================================

class AdminDashboardOverviewAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Dashboard"],
        responses=AdminOverviewSerializer,
    )
    def get(self, request):

        users_count = User.objects.count()

        products_count = Product.objects.count()

        orders_count = Order.objects.count()

        total_sales = (
            Payment.objects
            .filter(
                status=PaymentStatus.SUCCESS
            )
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
            or 0
        )

        data = {
            "users_count": users_count,
            "products_count": products_count,
            "orders_count": orders_count,
            "total_sales": total_sales,
        }

        serializer = AdminOverviewSerializer(data)

        return Response({
            "overview": serializer.data
        })