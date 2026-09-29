from django.db.models import Q
from django.utils.dateparse import parse_date

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from admin_panel.permissions import IsAdminPanelUser

from payment.models import (
    Payment,
    PaymentStatus,
    PaymentGateway,
)

from admin_panel.serializers.payments import (
    AdminPaymentListSerializer,
    AdminPaymentDetailSerializer,
)


# =========================================================
# PAYMENT LIST
# =========================================================

class AdminPaymentListAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Payments"],
        summary="لیست پرداخت‌ها",
        description=(
            "لیست پرداخت‌های ثبت‌شده را برای پنل مدیریت نمایش می‌دهد. "
            "امکان جستجو و فیلتر بر اساس وضعیت، درگاه و تاریخ وجود دارد."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "جستجو بر اساس نام گیرنده، "
                    "شماره موبایل، کد پیگیری سفارش، "
                    "شناسه سفارش، شناسه پرداخت، "
                    "Authority یا Reference ID"
                ),
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "وضعیت پرداخت: "
                    "pending / success / failed / canceled"
                ),
            ),
            OpenApiParameter(
                name="gateway",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "درگاه پرداخت. "
                    "در حال حاضر: zarinpal"
                ),
            ),
            OpenApiParameter(
                name="date_from",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="تاریخ شروع به فرمت YYYY-MM-DD",
            ),
            OpenApiParameter(
                name="date_to",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="تاریخ پایان به فرمت YYYY-MM-DD",
            ),
        ],
        responses={
            200: AdminPaymentListSerializer(many=True),
            400: OpenApiResponse(
                description="پارامترهای فیلتر نامعتبر هستند."
            ),
        },
    )
    def get(self, request):

        payments = (
            Payment.objects
            .select_related(
                "user",
                "order",
            )
            .all()
        )

        # =================================================
        # SEARCH
        # =================================================

        search = request.query_params.get(
            "search"
        )

        if search:

            search = search.strip()

            search_filter = (
                Q(order__recipient_name__icontains=search)
                |
                Q(user__phone_number__icontains=search)
                |
                Q(order__tracking_code__icontains=search)
                |
                Q(authority__icontains=search)
                |
                Q(reference_id__icontains=search)
            )

            if search.isdigit():

                search_filter |= Q(
                    id=int(search)
                )

                search_filter |= Q(
                    order_id=int(search)
                )

            payments = payments.filter(
                search_filter
            )

        # =================================================
        # STATUS FILTER
        # =================================================

        payment_status = request.query_params.get(
            "status"
        )

        if payment_status:

            valid_statuses = {
                value
                for value, _ in PaymentStatus.choices
            }

            if payment_status not in valid_statuses:

                return Response(
                    {
                        "success": False,
                        "message": "وضعیت پرداخت نامعتبر است.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payments = payments.filter(
                status=payment_status
            )

        # =================================================
        # GATEWAY FILTER
        # =================================================

        gateway = request.query_params.get(
            "gateway"
        )

        if gateway:

            valid_gateways = {
                value
                for value, _ in PaymentGateway.choices
            }

            if gateway not in valid_gateways:

                return Response(
                    {
                        "success": False,
                        "message": "درگاه پرداخت نامعتبر است.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payments = payments.filter(
                gateway=gateway
            )

        # =================================================
        # DATE FROM
        # =================================================

        date_from = request.query_params.get(
            "date_from"
        )

        if date_from:

            parsed_date_from = parse_date(
                date_from
            )

            if not parsed_date_from:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "تاریخ شروع نامعتبر است. "
                            "فرمت صحیح YYYY-MM-DD است."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payments = payments.filter(
                created_date__date__gte=parsed_date_from
            )

        # =================================================
        # DATE TO
        # =================================================

        date_to = request.query_params.get(
            "date_to"
        )

        if date_to:

            parsed_date_to = parse_date(
                date_to
            )

            if not parsed_date_to:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "تاریخ پایان نامعتبر است. "
                            "فرمت صحیح YYYY-MM-DD است."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payments = payments.filter(
                created_date__date__lte=parsed_date_to
            )

        # =================================================
        # RESPONSE
        # =================================================

        serializer = AdminPaymentListSerializer(
            payments,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# PAYMENT DETAIL
# =========================================================

class AdminPaymentDetailAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Payments"],
        summary="جزئیات پرداخت",
        description=(
            "جزئیات کامل یک پرداخت را برای پنل مدیریت نمایش می‌دهد."
        ),
        responses={
            200: AdminPaymentDetailSerializer,
            404: OpenApiResponse(
                description="پرداخت پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):

        try:

            payment = (
                Payment.objects
                .select_related(
                    "user",
                    "order",
                )
                .get(pk=pk)
            )

        except Payment.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "پرداخت مورد نظر پیدا نشد.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminPaymentDetailSerializer(
            payment
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )