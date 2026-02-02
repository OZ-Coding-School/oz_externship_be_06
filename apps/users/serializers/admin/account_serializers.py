from typing import Any
from rest_framework import serializers
from apps.users.models import User

class AdminAccountListSerializer(serializers.ModelSerializer[Any]):
    """
    어드민 페이지 회원 목록 조회를 위한 시리얼라이저
    """

    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f%z")

    class Meta:
        model = User
        fields = ["id", "email", "nickname", "name", "status", "role", "created_at"]

    def get_status(self, obj: User) -> str:
        if hasattr(obj, "withdrawal") and obj.withdrawal is not None:
            return "withdrew"
        return "active" if obj.is_active else "inactive"

    def get_role(self, obj: User) -> str:
        return obj.role.lower()