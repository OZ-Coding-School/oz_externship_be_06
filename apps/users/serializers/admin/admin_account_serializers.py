from typing import Any, Optional
from rest_framework import serializers
from apps.users.models import User

class AdminAccountListSerializer(serializers.ModelSerializer[User]):
    """
    어드민 페이지 회원 목록 조회용 시리얼라이저 (테스트 에러 해결 버전)
    """
    # 모델에 account_status/role_lower 프로퍼티가 없을 경우를 대비해 안정적인 메서드 필드 사용
    status = serializers.SerializerMethodField()
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

    def get_status(self, obj: User) -> str:
        # User 모델의 상태 로직을 안전하게 반환
        if hasattr(obj, 'withdrawal') and obj.withdrawal:
            return "WITHDREW"
        return "ACTIVATED" if obj.is_active else "DEACTIVATED"

    def get_role(self, obj: User) -> str:
        # 테스트 코드의 .lower() 비교를 위해 소문자로 반환
        return obj.role.lower() if obj.role else ""


class AdminAccountUpdateRequestSerializer(serializers.Serializer[Any]):
    """
    어드민 페이지 회원 정보 수정 요청 (입력 검증)
    """
    nickname = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=30, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    birthday = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=User.Gender.choices, required=False)
    profile_img_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    def validate_phone_number(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        if not value.isdigit():
            raise serializers.ValidationError("전화번호는 숫자만 입력 가능합니다.")
        if len(value) != 11:
            raise serializers.ValidationError("전화번호는 11자리 숫자로 구성되어야 합니다.")
        return value

    def _validate_stripped_text(self, field_name: str, value: Optional[str]) -> Optional[str]:
        if value is not None:
            stripped_value = value.strip()
            if not stripped_value:
                raise serializers.ValidationError(f"{field_name}은(는) 빈 값일 수 없습니다.")
            return stripped_value
        return value

    def validate_nickname(self, value: Optional[str]) -> Optional[str]:
        return self._validate_stripped_text("닉네임", value)

    def validate_name(self, value: Optional[str]) -> Optional[str]:
        return self._validate_stripped_text("이름", value)


class AdminAccountUpdateResponseSerializer(serializers.ModelSerializer[User]):
    """
    어드민 페이지 회원 정보 수정 결과 응답 전용
    """
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "role",
            "phone_number",
            "birthday",
            "gender",
            "gender_display",
            "profile_img_url",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields