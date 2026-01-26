from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers


# 비밀번호 변경 (로그인 상태)
class ChangePasswordSerializer(serializers.Serializer[dict[str, Any]]):

    old_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )

    def validate_new_password(self, value: str) -> str:
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value


# 비밀번호 분실 재설정 요청 스키마
class FindPasswordSerializer(serializers.Serializer[dict[str, Any]]):

    email_token = serializers.CharField(
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )

    def validate_new_password(self, value: str) -> str:
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value
