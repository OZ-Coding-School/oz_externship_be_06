from django.conf import settings
from rest_framework import serializers

from apps.users.models import User


class MeResponseSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    birthday = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z", required=False, allow_null=True)
    gender = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "gender",
            "profile_img_url",
            "created_at",
        )

    def get_gender(self, obj: User) -> str:
        return "M" if obj.gender == "MALE" else "F"


class MeUpdateRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    nickname = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=30, required=False)
    birthday = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=["M", "F"], required=False)


class MeUpdateResponseSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    birthday = serializers.DateField(format="%Y-%m-%d")
    gender = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nickname",
            "name",
            "birthday",
            "gender",
            "phone_number",
            "updated_at",
        )

    def get_gender(self, obj: User) -> str:
        return "M" if obj.gender == "MALE" else "F"


class ProfileImageUrlRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    profile_img_url = serializers.URLField(max_length=255)

    def validate_profile_img_url(self, value: str) -> str:
        custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)
        bucket_name = getattr(settings, "AWS_S3_BUCKET_NAME", "")
        region = getattr(settings, "AWS_S3_REGION", "")

        allowed_prefixes = []
        if custom_domain:
            allowed_prefixes.append(f"https://{custom_domain}/")
        if bucket_name and region:
            allowed_prefixes.append(f"https://{bucket_name}.s3.{region}.amazonaws.com/")

        if not any(value.startswith(prefix) for prefix in allowed_prefixes):
            raise serializers.ValidationError("허용되지 않은 이미지 URL입니다.")

        return value


class ChangePhoneRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    phone_verify_token = serializers.CharField()
