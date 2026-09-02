from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
)
from drf_spectacular.utils import extend_schema

class CartBaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        return Cart.objects.get_or_create(
            user=user
        )[0]

    def get_cart_queryset(self):
        return (
            Cart.objects
            .prefetch_related(
                "items__variant__product__images",
                "items__variant__size",
                "items__variant__color",
            )
        )

    def get_serialized_cart(self, cart, request):
        cart = self.get_cart_queryset().get(
            pk=cart.pk
        )

        return CartSerializer(
            cart,
            context={"request": request},
        ).data


class CartDetailAPIView(CartBaseAPIView):

    def get(self, request):
        cart = self.get_cart(request.user)

        return Response(
            self.get_serialized_cart(
                cart,
                request,
            )
        )


class CartAddItemAPIView(CartBaseAPIView):

    @extend_schema(
    request=AddCartItemSerializer,
    )
    @transaction.atomic
    def post(self, request):
        cart = (
            Cart.objects
            .select_for_update()
            .get_or_create(
                user=request.user
            )[0]
        )

        serializer = AddCartItemSerializer(
            data=request.data,
            context={
                "cart": cart,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        variant = serializer.validated_data["variant"]
        quantity = serializer.validated_data["quantity"]

        # قفل Variant برای جلوگیری از Race Condition
        variant = (
            variant.__class__
            .objects
            .select_for_update()
            .get(pk=variant.pk)
        )

        if not variant.is_active:
            return Response(
                {
                    "detail": "این محصول دیگر فعال نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if variant.stock <= 0:
            return Response(
                {
                    "detail": "این محصول موجود نیست."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = (
            CartItem.objects
            .select_for_update()
            .filter(
                cart=cart,
                variant=variant,
            )
            .first()
        )

        if item:
            new_quantity = item.quantity + quantity

            if new_quantity > variant.stock:
                return Response(
                    {
                        "detail": (
                            f"حداکثر تعداد قابل انتخاب "
                            f"{variant.stock} عدد است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            item.quantity = new_quantity
            item.save(
                update_fields=[
                    "quantity",
                    "updated_date",
                ]
            )

        else:
            if quantity > variant.stock:
                return Response(
                    {
                        "detail": (
                            f"حداکثر تعداد قابل انتخاب "
                            f"{variant.stock} عدد است."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=quantity,
            )

        return Response(
            self.get_serialized_cart(
                cart,
                request,
            ),
            status=status.HTTP_200_OK,
        )


class CartItemUpdateAPIView(CartBaseAPIView):

    @transaction.atomic
    def patch(self, request, pk):
        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            user=request.user,
        )

        item = get_object_or_404(
            CartItem.objects.select_for_update(),
            pk=pk,
            cart=cart,
        )

        serializer = UpdateCartItemSerializer(
            data=request.data,
            context={
                "item": item,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        variant = serializer.validated_data["variant"]
        quantity = serializer.validated_data["quantity"]

        variant = (
            variant.__class__
            .objects
            .select_for_update()
            .get(pk=variant.pk)
        )

        if quantity > variant.stock:
            return Response(
                {
                    "detail": (
                        f"حداکثر تعداد قابل انتخاب "
                        f"{variant.stock} عدد است."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.quantity = quantity

        item.save(
            update_fields=[
                "quantity",
                "updated_date",
            ]
        )

        return Response(
            self.get_serialized_cart(
                cart,
                request,
            )
        )


class CartItemDeleteAPIView(CartBaseAPIView):

    @transaction.atomic
    def delete(self, request, pk):
        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            user=request.user,
        )

        item = get_object_or_404(
            CartItem.objects.select_for_update(),
            pk=pk,
            cart=cart,
        )

        item.delete()

        return Response(
            {
                "detail": "محصول از سبد خرید حذف شد."
            },
            status=status.HTTP_200_OK,
        )


class CartClearAPIView(CartBaseAPIView):

    @transaction.atomic
    def delete(self, request):
        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            user=request.user,
        )

        cart.items.all().delete()

        return Response(
            {
                "detail": "سبد خرید با موفقیت خالی شد."
            },
            status=status.HTTP_200_OK,
        )