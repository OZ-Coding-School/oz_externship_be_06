import re
from typing import Any

from rest_framework import serializers


# 이메일 인증 발송 시리얼라이저
class SendEmailVerificationSerializer(serializers.Serializer[dict[str, Any]]):

    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "이메일을 입력해주세요.",
            "invalid": "올바른 이메일 형식이 아닙니다.",
        },
    )


# 이메일 인증 시리얼라이저
class VerifyEmailSerializer(serializers.Serializer[dict[str, Any]]):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "이메일을 입력해주세요.",
            "invalid": "올바른 이메일 형식이 아닙니다.",
        },
    )
    code = serializers.CharField(
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "인증 코드를 입력해주세요.",
        },
    )

    def validate_code(self, value: str) -> str:
        if not re.match(r"^[a-zA-Z0-9]{6}$", value):
            raise serializers.ValidationError("인증 코드는 6자리 영문/숫자여야 합니다.")
        return value
