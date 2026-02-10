from typing import Any

from rest_framework import serializers

from apps.users.models import User


class AdminAccountListSerializer(serializers.ModelSerializer[User]):
    """
    어드민 페이지 회원 목록 조회를 위한 시리얼라이저
    """

    # 모델의 property를 직접 연결하여 로직을 단순화
    status = serializers.ReadOnlyField(source="account_status")
    role = serializers.ReadOnlyField(source="role_lower")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f%z")

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "status",
            "role",
            "created_at",
        ]
