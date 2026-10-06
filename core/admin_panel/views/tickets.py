from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

from admin_panel.permissions import IsAdminPanelUser

from website.models import ContactMessage

from admin_panel.serializers.tickets import (
    AdminTicketListSerializer,
    AdminTicketDetailSerializer,
)


# =========================================================
# BASE VIEW
# =========================================================

class AdminTicketBaseView(APIView):

    permission_classes = (
        IsAuthenticated,
        IsAdminPanelUser,
    )


# =========================================================
# TICKET LIST
# =========================================================

class AdminTicketListView(AdminTicketBaseView):

    @extend_schema(
        tags=["Admin Panel - Tickets"],
        summary="لیست تیکت‌ها",
        description=(
            "نمایش لیست پیام‌های تماس با ما در پنل مدیریت. "
            "امکان جستجو و فیلتر بر اساس وضعیت مشاهده وجود دارد."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                required=False,
                description=(
                    "جستجو بر اساس نام، موضوع، شماره تلفن، "
                    "ایمیل یا متن پیام"
                ),
            ),
            OpenApiParameter(
                name="seen",
                type=bool,
                required=False,
                description="فیلتر بر اساس وضعیت مشاهده شدن تیکت",
            ),
        ],
        responses={
            200: AdminTicketListSerializer(many=True),
        },
    )
    def get(self, request):

        tickets = ContactMessage.objects.all()

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        search = request.query_params.get("search")

        if search:
            tickets = tickets.filter(
                Q(name__icontains=search)
                | Q(subject__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
                | Q(message__icontains=search)
            )

        # -------------------------------------------------
        # SEEN FILTER
        # -------------------------------------------------

        seen = request.query_params.get("seen")

        if seen is not None:

            if seen.lower() == "true":
                tickets = tickets.filter(seen=True)

            elif seen.lower() == "false":
                tickets = tickets.filter(seen=False)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        serializer = AdminTicketListSerializer(
            tickets,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =========================================================
# TICKET DETAIL
# =========================================================

class AdminTicketDetailView(AdminTicketBaseView):

    @extend_schema(
        tags=["Admin Panel - Tickets"],
        summary="جزئیات تیکت",
        description=(
            "نمایش جزئیات کامل تیکت و امکان تغییر وضعیت "
            "مشاهده شدن آن. در PATCH فقط فیلد seen قابل تغییر است."
        ),
        responses={
            200: AdminTicketDetailSerializer,
            404: OpenApiResponse(
                description="تیکت مورد نظر پیدا نشد.",
            ),
        },
    )
    def get(self, request, pk):

        try:
            ticket = ContactMessage.objects.get(pk=pk)

        except ContactMessage.DoesNotExist:

            return Response(
                {
                    "detail": "تیکت مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminTicketDetailSerializer(
            ticket,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Admin Panel - Tickets"],
        summary="تغییر وضعیت مشاهده تیکت",
        description=(
            "تغییر وضعیت مشاهده شدن تیکت. "
            "فقط فیلد seen قابل تغییر است."
        ),
        request=AdminTicketDetailSerializer,
        responses={
            200: AdminTicketDetailSerializer,
            400: OpenApiResponse(
                description="اطلاعات ارسال شده معتبر نیست.",
            ),
            404: OpenApiResponse(
                description="تیکت مورد نظر پیدا نشد.",
            ),
        },
    )
    def patch(self, request, pk):

        try:
            ticket = ContactMessage.objects.get(pk=pk)

        except ContactMessage.DoesNotExist:

            return Response(
                {
                    "detail": "تیکت مورد نظر پیدا نشد."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminTicketDetailSerializer(
            ticket,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )