from rest_framework import serializers


class RequestOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    def validate_phone_number(self, value):
        value = value.strip()

        # normalize +98
        if value.startswith("+98"):
            value = "0" + value[3:]

        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be exactly 11 digits.")

        return value
    
    
class VerifyOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=4)

    def validate_phone_number(self, value):
        value = value.strip()

        # normalize +98
        if value.startswith("+98"):
            value = "0" + value[3:]

        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be exactly 11 digits.")

        return value
    
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()