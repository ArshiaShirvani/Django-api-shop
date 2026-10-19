from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

import jdatetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from accounts.models import User
from accounts.sms import send_sms

from admin_panel.permissions import IsAdminPanelUser

from order.models import (
    Coupon,
    CouponUsage,
)

from admin_panel.serializers.coupons import (
    AdminCouponListSerializer,
    AdminCouponDetailSerializer,
    AdminCouponCreateSerializer,
    AdminCouponUpdateSerializer,
    AdminCouponUsageSerializer,
)


# =========================================================
# COUPON LIST
# =========================================================

class AdminCouponListAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="لیست کدهای تخفیف",
        description=(
            "لیست کدهای تخفیف را نمایش می‌دهد. "
            "امکان جستجو، فیلتر و مرتب‌سازی وجود دارد."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "جستجو بر اساس کد تخفیف "
                    "یا شماره موبایل کاربران مجاز"
                ),
            ),
            OpenApiParameter(
                name="discount_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "نوع تخفیف: "
                    "percentage / fixed"
                ),
            ),
            OpenApiParameter(
                name="is_global",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="عمومی یا اختصاصی بودن کد تخفیف",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="فعال یا غیرفعال بودن",
            ),
            OpenApiParameter(
                name="date_from",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="شروع بازه تاریخ",
            ),
            OpenApiParameter(
                name="date_to",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="پایان بازه تاریخ",
            ),
        ],
        responses={
            200: AdminCouponListSerializer(many=True),
            400: OpenApiResponse(
                description="پارامتر فیلتر نامعتبر است."
            ),
        },
    )
    def get(self, request):

        coupons = (
            Coupon.objects
            .prefetch_related("users")
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

            coupons = coupons.filter(
                Q(code__icontains=search)
                |
                Q(
                    users__phone_number__icontains=search
                )
            ).distinct()

        # =================================================
        # DISCOUNT TYPE
        # =================================================

        discount_type = request.query_params.get(
            "discount_type"
        )

        if discount_type:

            valid_types = {
                value
                for value, _
                in Coupon.DiscountType.choices
            }

            if discount_type not in valid_types:

                return Response(
                    {
                        "success": False,
                        "message": (
                            "نوع تخفیف نامعتبر است."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            coupons = coupons.filter(
                discount_type=discount_type
            )

        # =================================================
        # IS GLOBAL
        # =================================================

        is_global = request.query_params.get(
            "is_global"
        )

        if is_global is not None:

            if is_global.lower() not in (
                "true",
                "false",
            ):

                return Response(
                    {
                        "success": False,
                        "message": (
                            "مقدار is_global باید "
                            "true یا false باشد."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            coupons = coupons.filter(
                is_global=is_global.lower() == "true"
            )

        # =================================================
        # IS ACTIVE
        # =================================================

        is_active = request.query_params.get(
            "is_active"
        )

        if is_active is not None:

            if is_active.lower() not in (
                "true",
                "false",
            ):

                return Response(
                    {
                        "success": False,
                        "message": (
                            "مقدار is_active باید "
                            "true یا false باشد."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            coupons = coupons.filter(
                is_active=is_active.lower() == "true"
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

            coupons = coupons.filter(
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

            coupons = coupons.filter(
                created_date__date__lte=parsed_date_to
            )

        # =================================================
        # RESPONSE
        # =================================================

        serializer = AdminCouponListSerializer(
            coupons,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# COUPON CREATE
# =========================================================

class AdminCouponCreateAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="ایجاد کد تخفیف",
        description=(
            "یک کد تخفیف جدید ایجاد می‌کند و بلافاصله "
            "پیامک کد تخفیف را برای کاربران ارسال می‌کند. "
            "اگر کد همگانی باشد، پیامک برای تمام کاربران فعال ارسال می‌شود. "
            "اگر کد اختصاصی باشد، فقط برای کاربران انتخاب‌شده ارسال می‌شود."
        ),
        request=AdminCouponCreateSerializer,
        responses={
            201: AdminCouponDetailSerializer,
            400: OpenApiResponse(
                description="اطلاعات کد تخفیف نامعتبر است."
            ),
        },
    )
    def post(self, request):

        # =================================================
        # CREATE COUPON
        # =================================================

        serializer = AdminCouponCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        coupon = serializer.save()

        # =================================================
        # GET USERS
        # =================================================

        if coupon.is_global:

            users = (
                User.objects
                .filter(
                    is_active=True,
                )
                .select_related(
                    "profile",
                )
            )

        else:

            users = (
                coupon.users
                .filter(
                    is_active=True,
                )
                .select_related(
                    "profile",
                )
            )

        # =================================================
        # DISCOUNT TEXT
        # =================================================

        if (
            coupon.discount_type
            == Coupon.DiscountType.PERCENTAGE
        ):

            discount_text = (
                f"{coupon.discount_value}٪"
            )

        else:

            discount_text = (
                f"{coupon.discount_value:,} ریال"
            )

        # =================================================
        # MINIMUM ORDER TEXT
        # =================================================

        if coupon.minimum_order_amount > 0:

            minimum_order_text = (
                f"{coupon.minimum_order_amount:,} ریال"
            )

        else:

            minimum_order_text = "بدون حداقل خرید"

        # =================================================
        # END DATE - SHAMSI
        # =================================================

        end_datetime = timezone.localtime(
            coupon.end_date
        )

        jalali_end_datetime = (
            jdatetime.datetime.fromgregorian(
                datetime=end_datetime
            )
        )

        end_date = jalali_end_datetime.strftime(
            "%Y/%m/%d"
        )

        # =================================================
        # SEND SMS
        # =================================================

        sent_count = 0

        for user in users:

            profile = getattr(
                user,
                "profile",
                None,
            )

            if profile:

                customer_name = (
                    profile.get_fullname()
                )

            else:

                customer_name = "کاربر"

            if customer_name == "کاربر جدید":

                customer_name = "کاربر"

            # =================================================
            # SMS TEXT
            # =================================================

            coupon_sms = (
                f"{customer_name} عزیز،\n\n"
                "یک کد تخفیف ویژه برای شما فعال شده است 🎁\n\n"
                f"کد تخفیف: {coupon.code}\n"
                f"میزان تخفیف: {discount_text}\n"
                f"حداقل خرید: {minimum_order_text}\n"
                f"اعتبار تا: {end_date}\n\n"
                "برای استفاده از این کد، "
                "هنگام ثبت سفارش آن را وارد کنید.\n\n"
                "فروشگاه لوما"
            )

            send_sms(
                to=user.phone_number,
                text=coupon_sms,
            )

            sent_count += 1

        # =================================================
        # GET FRESH COUPON
        # =================================================

        coupon = (
            Coupon.objects
            .prefetch_related(
                "users",
            )
            .get(
                pk=coupon.pk
            )
        )

        # =================================================
        # RESPONSE
        # =================================================

        response_data = (
            AdminCouponDetailSerializer(
                coupon
            ).data
        )

        response_data["sms_sent_count"] = (
            sent_count
        )

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


# =========================================================
# COUPON DETAIL
# =========================================================

class AdminCouponDetailAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="جزئیات کد تخفیف",
        description=(
            "جزئیات کامل یک کد تخفیف را نمایش می‌دهد."
        ),
        responses={
            200: AdminCouponDetailSerializer,
            404: OpenApiResponse(
                description="کد تخفیف پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):

        try:

            coupon = (
                Coupon.objects
                .prefetch_related(
                    "users",
                )
                .get(pk=pk)
            )

        except Coupon.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": (
                        "کد تخفیف مورد نظر پیدا نشد."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminCouponDetailSerializer(
            coupon
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# COUPON UPDATE
# =========================================================

class AdminCouponUpdateAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="ویرایش کد تخفیف",
        description=(
            "کد تخفیف را به صورت کامل یا جزئی "
            "ویرایش می‌کند."
        ),
        request=AdminCouponUpdateSerializer,
        responses={
            200: AdminCouponDetailSerializer,
            400: OpenApiResponse(
                description="اطلاعات نامعتبر است."
            ),
            404: OpenApiResponse(
                description="کد تخفیف پیدا نشد."
            ),
        },
    )
    def put(self, request, pk):

        return self._update(
            request,
            pk,
            partial=False,
        )

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="ویرایش جزئی کد تخفیف",
        description=(
            "بخشی از اطلاعات کد تخفیف را ویرایش می‌کند."
        ),
        request=AdminCouponUpdateSerializer,
        responses={
            200: AdminCouponDetailSerializer,
            400: OpenApiResponse(
                description="اطلاعات نامعتبر است."
            ),
            404: OpenApiResponse(
                description="کد تخفیف پیدا نشد."
            ),
        },
    )
    def patch(self, request, pk):

        return self._update(
            request,
            pk,
            partial=True,
        )

    def _update(
        self,
        request,
        pk,
        partial=False,
    ):

        try:

            coupon = Coupon.objects.get(
                pk=pk
            )

        except Coupon.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": (
                        "کد تخفیف مورد نظر پیدا نشد."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminCouponUpdateSerializer(
            coupon,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        coupon = serializer.save()

        coupon = (
            Coupon.objects
            .prefetch_related("users")
            .get(pk=coupon.pk)
        )

        return Response(
            AdminCouponDetailSerializer(
                coupon
            ).data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# COUPON DELETE
# =========================================================

class AdminCouponDeleteAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="حذف کد تخفیف",
        description=(
            "کد تخفیف را حذف می‌کند. "
            "اگر این کد در سفارش‌ها یا سوابق مصرف استفاده شده باشد، "
            "به دلیل محدودیت‌های مدل ممکن است حذف امکان‌پذیر نباشد."
        ),
        responses={
            204: OpenApiResponse(
                description="کد تخفیف با موفقیت حذف شد."
            ),
            400: OpenApiResponse(
                description="کد تخفیف قابل حذف نیست."
            ),
            404: OpenApiResponse(
                description="کد تخفیف پیدا نشد."
            ),
        },
    )
    def delete(self, request, pk):

        try:

            coupon = Coupon.objects.get(
                pk=pk
            )

        except Coupon.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": (
                        "کد تخفیف مورد نظر پیدا نشد."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:

            coupon.delete()

        except Exception:

            return Response(
                {
                    "success": False,
                    "message": (
                        "این کد تخفیف به اطلاعات دیگری "
                        "وابسته است و قابل حذف نیست."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# =========================================================
# COUPON USAGE LIST
# =========================================================

class AdminCouponUsageListAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="لیست مصرف کدهای تخفیف",
        description=(
            "سوابق مصرف کدهای تخفیف را نمایش می‌دهد."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "جستجو بر اساس کد تخفیف، "
                    "شماره موبایل یا کد پیگیری سفارش"
                ),
            ),
            OpenApiParameter(
                name="date_from",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="تاریخ شروع",
            ),
            OpenApiParameter(
                name="date_to",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="تاریخ پایان",
            ),
        ],
        responses={
            200: AdminCouponUsageSerializer(many=True),
            400: OpenApiResponse(
                description="پارامتر تاریخ نامعتبر است."
            ),
        },
    )
    def get(self, request):

        usages = (
            CouponUsage.objects
            .select_related(
                "coupon",
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

            usages = usages.filter(
                Q(coupon__code__icontains=search)
                |
                Q(
                    user__phone_number__icontains=search
                )
                |
                Q(
                    order__tracking_code__icontains=search
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

            usages = usages.filter(
                used_date__date__gte=parsed_date_from
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

            usages = usages.filter(
                used_date__date__lte=parsed_date_to
            )

        serializer = AdminCouponUsageSerializer(
            usages,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# COUPON USAGE DETAIL
# =========================================================

class AdminCouponUsageDetailAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Coupons"],
        summary="جزئیات مصرف کد تخفیف",
        description=(
            "جزئیات یک سابقه مصرف کد تخفیف را نمایش می‌دهد."
        ),
        responses={
            200: AdminCouponUsageSerializer,
            404: OpenApiResponse(
                description="سابقه مصرف پیدا نشد."
            ),
        },
    )
    def get(self, request, pk):

        try:

            usage = (
                CouponUsage.objects
                .select_related(
                    "coupon",
                    "user",
                    "order",
                )
                .get(pk=pk)
            )

        except CouponUsage.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": (
                        "سابقه مصرف کد تخفیف پیدا نشد."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminCouponUsageSerializer(
            usage
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )