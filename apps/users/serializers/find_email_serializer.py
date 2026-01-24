from typing import Any

from rest_framework import serializers


# 이메일 찾기
class FindEmailSerializer(serializers.Serializer[dict[str, Any]]):

    name = serializers.CharField(
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )
    sms_token = serializers.CharField(
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )
