from __future__ import annotations

import re
from typing import Any

from rest_framework import serializers


# SMS 인증 발송 요청
class SendSmsVerificationSerializer(serializers.Serializer[dict[str, Any]]):

    phone_number = serializers.CharField(
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "휴대폰 번호를 입력해주세요.",
        },
    )

    def validate_phone_number(self, value: str) -> str:
        if not re.match(r"^\d{11}$", value):
            raise serializers.ValidationError("11자리 숫자로 구성된 휴대폰 번호를 입력해주세요.")
        return value


# 확인 요청 스키마
class VerifySmsSerializer(serializers.Serializer[dict[str, Any]]):

    phone_number = serializers.CharField(
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "휴대폰 번호를 입력해주세요.",
        },
    )
    code = serializers.CharField(
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "인증 코드를 입력해주세요.",
        },
    )

    def validate_phone_number(self, value: str) -> str:
        if not re.match(r"^\d{11}$", value):
            raise serializers.ValidationError("11자리 숫자로 구성된 휴대폰 번호를 입력해주세요.")
        return value

    def validate_code(self, value: str) -> str:
        if not re.match(r"^\d{6}$", value):
            raise serializers.ValidationError("인증 코드는 6자리 숫자여야 합니다.")
        return value
