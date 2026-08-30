from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Review
from .serializers import ReviewSerializer
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")

        return Review.objects.filter(
            product_id=product_id
        ).select_related("user", "product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewUpdateView(generics.UpdateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user
        ).select_related("user", "product")
        
        
class ReviewDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        review = get_object_or_404(
            Review,
            pk=pk,
            user=request.user
        )

        review.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )