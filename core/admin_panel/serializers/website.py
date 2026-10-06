from rest_framework import serializers

from website.models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory,
)


# ==========================================================
# WEBSITE SETTING
# ==========================================================

class AdminWebsiteSettingSerializer(serializers.ModelSerializer):

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteSetting

        fields = (
            "id",
            "title",
            "logo",
            "logo_url",
            "description",
            "phone",
            "email",
            "address",
            "latitude",
            "longitude",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "logo_url",
            "created_date",
            "updated_date",
        )

    def get_logo_url(self, obj):

        if not obj.logo:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.logo.url)

        return obj.logo.url


# ==========================================================
# HOME BANNER
# ==========================================================

class AdminHomeBannerSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()
    phone_banner_url = serializers.SerializerMethodField()

    class Meta:
        model = HomeBanner

        fields = (
            "id",
            "title",
            "image",
            "image_url",
            "phone_bannner",
            "phone_banner_url",
            "link",
            "is_active",
            "is_first",
            "order",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "image_url",
            "phone_banner_url",
            "created_date",
            "updated_date",
        )

    def get_image_url(self, obj):

        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url

    def get_phone_banner_url(self, obj):

        if not obj.phone_bannner:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.phone_bannner.url
            )

        return obj.phone_bannner.url


# ==========================================================
# SECONDARY BANNER
# ==========================================================

class AdminSecondaryBannerSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SecondaryBanner

        fields = (
            "id",
            "title",
            "image",
            "image_url",
            "link",
            "is_active",
            "order",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "image_url",
            "created_date",
            "updated_date",
        )

    def get_image_url(self, obj):

        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url


# ==========================================================
# HOME CATEGORY
# ==========================================================

class AdminHomeCategorySerializer(serializers.ModelSerializer):

    category_title = serializers.CharField(
        source="category.title",
        read_only=True,
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = HomeCategory

        fields = (
            "id",
            "category",
            "category_title",
            "custom_title",
            "image",
            "image_url",
            "is_active",
            "created_date",
            "updated_date",
        )

        read_only_fields = (
            "id",
            "category_title",
            "image_url",
            "created_date",
            "updated_date",
        )

    def get_image_url(self, obj):

        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url