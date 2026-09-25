from rest_framework import serializers


# =========================================================
# DASHBOARD OVERVIEW
# =========================================================

class AdminOverviewSerializer(serializers.Serializer):

    users_count = serializers.IntegerField()

    products_count = serializers.IntegerField()

    orders_count = serializers.IntegerField()

    total_sales = serializers.IntegerField()