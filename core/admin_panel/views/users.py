from django.db.models import Q, Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from accounts.models import User
from payment.models import Payment, PaymentStatus

from ..permissions import IsAdminPanelUser

from ..serializers.users import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminUserStatusSerializer,
)


# =========================================================
# USERS LIST
# =========================================================

class AdminUserListAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Users"],
        parameters=[
            OpenApiParameter(
                name="search",
                description=(
                    "جستجو بر اساس شماره تلفن، نام یا نام خانوادگی"
                ),
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="is_active",
                description="فیلتر وضعیت فعال بودن کاربر",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="role",
                description="فیلتر بر اساس نقش کاربر",
                required=False,
                type=OpenApiTypes.STR,
                enum=["user", "admin"],
            ),
            OpenApiParameter(
                name="page",
                description="شماره صفحه",
                required=False,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="page_size",
                description="تعداد کاربران در هر صفحه",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ],
        responses=AdminUserListSerializer(many=True),
    )
    def get(self, request):

        users = (
            User.objects
            .select_related("profile")
            .all()
            .order_by("-created_date")
        )

        # =====================================================
        # SEARCH
        # =====================================================

        search = request.query_params.get("search")

        if search:

            users = users.filter(
                Q(phone_number__icontains=search)
                | Q(profile__first_name__icontains=search)
                | Q(profile__last_name__icontains=search)
            )

        # =====================================================
        # ACTIVE FILTER
        # =====================================================

        is_active = request.query_params.get("is_active")

        if is_active in ["true", "false"]:

            users = users.filter(
                is_active=(is_active == "true")
            )

        # =====================================================
        # ROLE FILTER
        # =====================================================

        role = request.query_params.get("role")

        if role:

            users = users.filter(
                role=role
            )

        # =====================================================
        # PAGINATION
        # =====================================================

        paginator = PageNumberPagination()

        paginator.page_size = 20

        page_size = request.query_params.get("page_size")

        if page_size:

            try:

                page_size = int(page_size)

                if 1 <= page_size <= 100:
                    paginator.page_size = page_size

            except (TypeError, ValueError):

                pass

        page = paginator.paginate_queryset(
            users,
            request
        )

        results = []

        for user in page:

            profile = getattr(
                user,
                "profile",
                None
            )

            results.append({
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name": (
                    profile.first_name
                    if profile
                    else None
                ),
                "last_name": (
                    profile.last_name
                    if profile
                    else None
                ),
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_date": user.created_date,
            })

        serializer = AdminUserListSerializer(
            results,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# =========================================================
# USER DETAIL
# =========================================================

class AdminUserDetailAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Users"],
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                description="شناسه کاربر",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        responses=AdminUserDetailSerializer,
    )
    def get(self, request, pk):

        try:

            user = (
                User.objects
                .select_related("profile")
                .get(pk=pk)
            )

        except User.DoesNotExist:

            return Response(
                {
                    "detail": "کاربر مورد نظر پیدا نشد."
                },
                status=404
            )

        profile = getattr(
            user,
            "profile",
            None
        )

        orders_count = user.orders.count()

        total_purchases = (
            Payment.objects
            .filter(
                user=user,
                status=PaymentStatus.SUCCESS
            )
            .aggregate(
                total=Sum("amount")
            )
            .get("total")
            or 0
        )

        data = {
            "id": user.id,
            "phone_number": user.phone_number,
            "first_name": (
                profile.first_name
                if profile
                else None
            ),
            "last_name": (
                profile.last_name
                if profile
                else None
            ),
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_date": user.created_date,
            "orders_count": orders_count,
            "total_purchases": total_purchases,
        }

        serializer = AdminUserDetailSerializer(data)

        return Response(
            serializer.data
        )


# =========================================================
# USER STATUS
# =========================================================

class AdminUserStatusAPIView(APIView):

    permission_classes = [IsAdminPanelUser]

    @extend_schema(
        tags=["Admin Panel - Users"],
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                description="شناسه کاربر",
                required=True,
                type=OpenApiTypes.INT,
            ),
        ],
        request=AdminUserStatusSerializer,
        responses=AdminUserStatusSerializer,
    )
    def patch(self, request, pk):

        try:

            user = User.objects.get(
                pk=pk
            )

        except User.DoesNotExist:

            return Response(
                {
                    "detail": "کاربر مورد نظر پیدا نشد."
                },
                status=404
            )

        serializer = AdminUserStatusSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user.is_active = serializer.validated_data[
            "is_active"
        ]

        user.save(
            update_fields=[
                "is_active",
                "updated_date",
            ]
        )

        return Response({
            "message": "وضعیت کاربر با موفقیت تغییر کرد.",
            "is_active": user.is_active,
        })