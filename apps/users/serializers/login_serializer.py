from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User


class LoginSerializer(serializers.Serializer[dict[str, Any]]):
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError({"detail": "이메일 또는 비밀번호가 올바르지 않습니다."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "비활성화된 계정입니다."})

        attrs["user"] = user
        return attrs

    def create(self, validated_data: dict[str, Any]) -> dict[str, str]:
        user: User = validated_data["user"]
        access_token = AccessToken.for_user(user)
        return {"access_token": str(access_token)}
