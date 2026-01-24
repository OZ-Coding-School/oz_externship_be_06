from typing import Any

from rest_framework import serializers

#JWT 토큰 재발급 요청
class TokenRefreshRequestSerializer(serializers.Serializer[dict[str, Any]]):

    refresh_token = serializers.CharField(
        required=True,
        error_messages={"required": "이 필드는 필수 항목입니다."},
    )
