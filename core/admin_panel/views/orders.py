from django.db.models import Q
from django.utils.dateparse import parse_date

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from order.models import (
    Order,
    OrderStatus,
)

from admin_panel.permissions import IsAdminPanelUser

from admin_panel.serializers.orders import (
    AdminOrderListSerializer,
    AdminOrderDetailSerializer,
    AdminOrderStatusUpdateSerializer,
)


# =========================================================
# ORDER STATUS TRANSITIONS
# =========================================================

ALLOWED_ORDER_STATUS_TRANSITIONS = {

    OrderStatus.PENDING: {
        OrderStatus.PAID,
        OrderStatus.CANCELLED,
    },

    OrderStatus.PAID: {
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED,
    },

    OrderStatus.PROCESSING: {
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    },

    OrderStatus.SHIPPED: {
        OrderStatus.DELIVERED,
    },

    OrderStatus.DELIVERED: set(),

    OrderStatus.CANCELLED: set(),
}


# =========================================================
# ORDER LIST
# =========================================================

@extend_schema(
    tags=["Admin Panel - Orders"],
    summary="لیست سفارش‌های پنل مدیریت",
    description=(
        "دریافت لیست سفارش‌ها با امکان جستجو و فیلتر بر اساس "
        "نام گیرنده، شماره تلفن، کد پیگیری، شناسه سفارش، "
        "نام محصول، وضعیت سفارش، وضعیت پرداخت، روش ارسال و بازه تاریخ."
    ),
    parameters=[
        OpenApiParameter(
            name="search",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "جستجو بر اساس نام گیرنده، شماره تلفن، "
                "کد پیگیری، شناسه سفارش یا نام محصول."
            ),
            examples=[
                OpenApiExample(
                    "نام محصول",
                    value="اسپرت بافت ست",
                ),
                OpenApiExample(
                    "کد پیگیری",
                    value="ORD-FCCA9313B7A6",
                ),
                OpenApiExample(
                    "شناسه سفارش",
                    value="3",
                ),
            ],
        ),

        OpenApiParameter(
            name="status",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="فیلتر بر اساس وضعیت سفارش.",
            enum=[
                "pending",
                "paid",
                "processing",
                "shipped",
                "delivered",
                "cancelled",
            ],
        ),

        OpenApiParameter(
            name="payment_status",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="فیلتر بر اساس وضعیت پرداخت.",
            enum=[
                "paid",
                "pending",
            ],
        ),

        OpenApiParameter(
            name="shipping_method",
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description="شناسه روش ارسال.",
        ),

        OpenApiParameter(
            name="date_from",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="تاریخ شروع بازه. فرمت: YYYY-MM-DD",
        ),

        OpenApiParameter(
            name="date_to",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="تاریخ پایان بازه. فرمت: YYYY-MM-DD",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=AdminOrderListSerializer(many=True),
            description="لیست سفارش‌ها با موفقیت دریافت شد.",
        ),

        400: OpenApiResponse(
            description="پارامترهای ارسال‌شده نامعتبر هستند.",
        ),
    },
)
class AdminOrderListAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    def get(self, request):

        orders = (
            Order.objects
            .select_related(
                "user",
                "shipping_method",
                "coupon",
            )
            .prefetch_related(
                "items",
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

            if search:

                search_query = (
                    Q(recipient_name__icontains=search)
                    |
                    Q(recipient_phone__icontains=search)
                    |
                    Q(tracking_code__icontains=search)
                    |
                    Q(items__product_title__icontains=search)
                )

                if search.isdigit():

                    search_query |= Q(
                        id=int(search)
                    )

                orders = orders.filter(
                    search_query
                ).distinct()

        # =================================================
        # ORDER STATUS
        # =================================================

        order_status = request.query_params.get(
            "status"
        )

        if order_status:

            valid_statuses = {
                value
                for value, label
                in OrderStatus.choices
            }

            if order_status not in valid_statuses:

                return Response(
                    {
                        "detail": (
                            "وضعیت سفارش نامعتبر است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            orders = orders.filter(
                status=order_status
            )

        # =================================================
        # PAYMENT STATUS
        # =================================================

        payment_status = request.query_params.get(
            "payment_status"
        )

        if payment_status:

            if payment_status not in [
                "paid",
                "pending",
            ]:

                return Response(
                    {
                        "detail": (
                            "وضعیت پرداخت نامعتبر است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            paid_statuses = [
                OrderStatus.PAID,
                OrderStatus.PROCESSING,
                OrderStatus.SHIPPED,
                OrderStatus.DELIVERED,
            ]

            if payment_status == "paid":

                orders = orders.filter(
                    status__in=paid_statuses
                )

            else:

                orders = orders.exclude(
                    status__in=paid_statuses
                )

        # =================================================
        # SHIPPING METHOD
        # =================================================

        shipping_method = request.query_params.get(
            "shipping_method"
        )

        if shipping_method:

            if not shipping_method.isdigit():

                return Response(
                    {
                        "detail": (
                            "شناسه روش ارسال نامعتبر است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            orders = orders.filter(
                shipping_method_id=int(
                    shipping_method
                )
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

            if parsed_date_from is None:

                return Response(
                    {
                        "detail": (
                            "فرمت تاریخ شروع نامعتبر است. "
                            "فرمت صحیح: YYYY-MM-DD"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            orders = orders.filter(
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

            if parsed_date_to is None:

                return Response(
                    {
                        "detail": (
                            "فرمت تاریخ پایان نامعتبر است. "
                            "فرمت صحیح: YYYY-MM-DD"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            orders = orders.filter(
                created_date__date__lte=parsed_date_to
            )

        # =================================================
        # SERIALIZE
        # =================================================

        serializer = AdminOrderListSerializer(
            orders,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# ORDER DETAIL
# =========================================================

@extend_schema(
    tags=["Admin Panel - Orders"],
    summary="جزئیات سفارش",
    description=(
        "دریافت اطلاعات کامل یک سفارش شامل اطلاعات مشتری، "
        "آدرس سفارش، محصولات، مبالغ، کد تخفیف، روش ارسال "
        "و وضعیت پرداخت."
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="شناسه سفارش.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=AdminOrderDetailSerializer,
            description="جزئیات سفارش با موفقیت دریافت شد.",
        ),

        404: OpenApiResponse(
            description="سفارش موردنظر پیدا نشد.",
        ),
    },
)
class AdminOrderDetailAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    def get(self, request, pk):

        try:

            order = (
                Order.objects
                .select_related(
                    "user",
                    "shipping_method",
                    "coupon",
                )
                .prefetch_related(
                    "items",
                )
                .get(
                    pk=pk
                )
            )

        except Order.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "سفارش موردنظر پیدا نشد."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminOrderDetailSerializer(
            order
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# ORDER STATUS UPDATE
# =========================================================

@extend_schema(
    tags=["Admin Panel - Orders"],
    summary="تغییر وضعیت سفارش",
    description=(
        "تغییر وضعیت سفارش توسط مدیر. "
        "Backend فقط Transitionهای مجاز را قبول می‌کند و "
        "از تغییر وضعیت‌های غیرمجاز جلوگیری می‌کند."
    ),
    parameters=[
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="شناسه سفارش.",
        ),
    ],
    request=AdminOrderStatusUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="وضعیت سفارش با موفقیت تغییر کرد.",
            examples=[
                OpenApiExample(
                    "موفق",
                    value={
                        "message": (
                            "وضعیت سفارش با موفقیت تغییر کرد."
                        ),
                        "status": "processing",
                    },
                ),
            ],
        ),

        400: OpenApiResponse(
            description="تغییر وضعیت مجاز نیست.",
            examples=[
                OpenApiExample(
                    "Transition نامعتبر",
                    value={
                        "detail": (
                            "تغییر وضعیت سفارش از "
                            "«تحویل داده شده» به "
                            "«در حال پردازش» مجاز نیست."
                        )
                    },
                ),
            ],
        ),

        404: OpenApiResponse(
            description="سفارش موردنظر پیدا نشد.",
            examples=[
                OpenApiExample(
                    "سفارش پیدا نشد",
                    value={
                        "detail": (
                            "سفارش موردنظر پیدا نشد."
                        )
                    },
                ),
            ],
        ),
    },
)
class AdminOrderStatusUpdateAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    def patch(self, request, pk):

        # =================================================
        # GET ORDER
        # =================================================

        try:

            order = Order.objects.get(
                pk=pk
            )

        except Order.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "سفارش موردنظر پیدا نشد."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =================================================
        # VALIDATE REQUEST
        # =================================================

        serializer = AdminOrderStatusUpdateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data[
            "status"
        ]

        current_status = order.status

        # =================================================
        # SAME STATUS
        # =================================================

        if current_status == new_status:

            return Response(
                {
                    "detail": (
                        "وضعیت سفارش در حال حاضر "
                        "همین مقدار است."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # CHECK TRANSITION
        # =================================================

        allowed_statuses = (
            ALLOWED_ORDER_STATUS_TRANSITIONS.get(
                current_status,
                set(),
            )
        )

        if new_status not in allowed_statuses:

            current_status_label = dict(
                OrderStatus.choices
            ).get(
                current_status,
                current_status,
            )

            new_status_label = dict(
                OrderStatus.choices
            ).get(
                new_status,
                new_status,
            )

            return Response(
                {
                    "detail": (
                        f"تغییر وضعیت سفارش از "
                        f"«{current_status_label}» به "
                        f"«{new_status_label}» "
                        f"مجاز نیست."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # UPDATE STATUS
        # =================================================

        order.status = new_status

        order.save(
            update_fields=[
                "status",
                "updated_date",
            ]
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {
                "message": (
                    "وضعیت سفارش با موفقیت تغییر کرد."
                ),
                "status": order.status,
            },
            status=status.HTTP_200_OK,
        )