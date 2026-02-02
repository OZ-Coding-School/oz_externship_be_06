from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

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
        email: str = attrs["email"]
        password: str = attrs["password"]

        # 먼저 유저 존재 여부 확인
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "이메일 또는 비밀번호가 올바르지 않습니다."})

        #비활성화된 계정은 별도 처리를 위해 플래그 설정
        if not user.is_active:
            attrs["user"] = user
            attrs["is_inactive"] = True
            return attrs

        # 비밀번호 검증
        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "이메일 또는 비밀번호가 올바르지 않습니다."})

        attrs["user"] = user
        return attrs

    def create(self, validated_data: dict[str, Any]) -> dict[str, str]:
        user: User = validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }
