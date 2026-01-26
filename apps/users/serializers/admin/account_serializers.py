from typing import Any

from rest_framework import serializers

from apps.users.models import User


class AdminAccountListSerializer(serializers.ModelSerializer[Any]):
    """
    어드민 페이지 회원 목록 조회를 위한 시리얼라이저
    """

    # 명세서의 status (active, inactive, withdrew) 대응
    status = serializers.SerializerMethodField()
    # 명세서의 role (user, staff, admin, student) 소문자 대응
    role = serializers.SerializerMethodField()
    birthday = serializers.DateField(format="%Y-%m-%d")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f%z")

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "birthday",
            "status",
            "role",
            "created_at",
        ]

    def get_status(self, obj: User) -> str:
        # Withdrawal 모델과 OneToOne 관계를 확인하여 탈퇴 여부 판단
        if hasattr(obj, "withdrawal") and obj.withdrawal is not None:
            return "withdrew"
        return "active" if obj.is_active else "inactive"

    def get_role(self, obj: User) -> str:
        # 모델의 대문자 Role을 명세서의 소문자 형식으로 변환
        return obj.role.lower()
