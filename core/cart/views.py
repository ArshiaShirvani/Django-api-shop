from django.shortcuts import render
from rest_framework.views import APIView


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Cart, CartItem
from .serializers import CartSerializer, AddCartItemSerializer
from shop.models import ProductVariant


class CartDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = Cart.objects.prefetch_related(
            "items__variant__product__images",
            "items__variant__size",
            "items__variant__color",
        ).get(pk=cart.pk)

        return Response(CartSerializer(cart).data)


class CartAddItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        serializer = AddCartItemSerializer(
            data=request.data,
            context={"cart": cart}
        )
        serializer.is_valid(raise_exception=True)

        variant = serializer.validated_data["variant"]
        quantity = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant
        )

        item.quantity = quantity if created else item.quantity + quantity
        item.save()

        return Response(CartSerializer(cart).data)


class CartItemUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)

        quantity = int(request.data.get("quantity", 1))

        if quantity < 1:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if quantity > item.variant.stock:
            return Response(
                {"detail": "موجودی کافی نیست"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.quantity = quantity
        item.save()

        return Response(CartSerializer(cart).data)



class CartItemDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
