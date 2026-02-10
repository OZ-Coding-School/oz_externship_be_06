from typing import Any

from rest_framework import serializers

from apps.users.models import User


class AdminAccountListSerializer(serializers.ModelSerializer[User]):
    """
    어드민 페이지 회원 목록 조회를 위한 시리얼라이저
    """

    # account_status 프로퍼티가 모델에 있다고 가정하고 유지합니다.
    status = serializers.ReadOnlyField(source="account_status")

    # role_lower 프로퍼티 대신 SerializerMethodField를 사용하여 안전하게 처리합니다.
    role = serializers.SerializerMethodField()

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

    def get_role(self, obj: User) -> str:
        # 모델의 role 필드 값을 가져와 소문자로 변환 (테스트 기대치인 'ta', 'om' 등에 대응)
        if not obj.role:
            return ""
        return obj.role.lower()
