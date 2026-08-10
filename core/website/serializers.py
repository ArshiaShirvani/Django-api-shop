from rest_framework import serializers

from .models import (
    WebsiteSetting,
    HomeBanner,
    SecondaryBanner,
    HomeCategory
)



# ==========================
# WEBSITE SETTINGS
# ==========================

class WebsiteSettingSerializer(serializers.ModelSerializer):

    logo = serializers.SerializerMethodField()


    class Meta:

        model = WebsiteSetting

        fields = [
            "title",
            "logo",
            "description",
            "phone",
            "email",
            "address",
            "latitude",
            "longitude",
        ]



    def get_logo(self, obj):

        if obj.logo:

            request = self.context.get("request")

            if request:

                return request.build_absolute_uri(
                    obj.logo.url
                )

            return obj.logo.url

        return None





# ==========================
# HOME BANNER
# ==========================

class HomeBannerSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()


    class Meta:

        model = HomeBanner

        fields = [
            "id",
            "title",
            "image",
            "link",
            "is_first",
        ]



    def get_image(self,obj):

        if obj.image:

            request = self.context.get("request")

            if request:

                return request.build_absolute_uri(
                    obj.image.url
                )

            return obj.image.url

        return None





# ==========================
# SECONDARY BANNER
# ==========================

class SecondaryBannerSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()


    class Meta:

        model = SecondaryBanner

        fields = [
            "id",
            "title",
            "image",
            "link",
        ]



    def get_image(self,obj):

        if obj.image:

            request = self.context.get("request")

            if request:

                return request.build_absolute_uri(
                    obj.image.url
                )

            return obj.image.url

        return None





# ==========================
# HOME CATEGORY
# ==========================

class HomeCategorySerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()

    image = serializers.SerializerMethodField()

    category_slug = serializers.CharField(
        source="category.slug",
        read_only=True
    )


    class Meta:

        model = HomeCategory

        fields = [
            "id",
            "category",
            "category_slug",
            "title",
            "image",
        ]



    def get_title(self,obj):

        if obj.custom_title:

            return obj.custom_title

        return obj.category.title



    def get_image(self,obj):

        if obj.image:

            request = self.context.get("request")

            if request:

                return request.build_absolute_uri(
                    obj.image.url
                )

            return obj.image.url


        return None