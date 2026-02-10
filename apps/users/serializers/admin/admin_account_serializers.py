from typing import Any, Dict, Optional

from rest_framework import serializers

from apps.users.models import User


class AdminAccountUpdateRequestSerializer(serializers.Serializer[Any]):
    """
    어드민 페이지 회원 정보 수정 요청 시리얼라이저
    """

    nickname = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=30, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    birthday = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=User.Gender.choices, required=False)
    profile_img_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    def validate_phone_number(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return value

        # 숫자 이외의 문자 제거 및 길이 검증
        if not value.isdigit():
            raise serializers.ValidationError("전화번호는 숫자만 입력 가능합니다.")
        if len(value) != 11:
            raise serializers.ValidationError("전화번호는 11자리 숫자로 구성되어야 합니다.")
        return value

    def validate_nickname(self, value: Optional[str]) -> Optional[str]:
        if value is not None:
            stripped_value = value.strip()
            if not stripped_value:
                raise serializers.ValidationError("닉네임은 빈 값일 수 없습니다.")
            return stripped_value
        return value

    def validate_name(self, value: Optional[str]) -> Optional[str]:
        if value is not None:
            stripped_value = value.strip()
            if not stripped_value:
                raise serializers.ValidationError("이름은 빈 값일 수 없습니다.")
            return stripped_value
        return value


class AdminAccountUpdateResponseSerializer(serializers.ModelSerializer[User]):
    """
    어드민 페이지 회원 정보 수정 성공 응답 시리얼라이저
    """

    # ChoiceField의 display text를 반환하도록 설정
    gender = serializers.CharField(source="get_gender_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "gender",
            "profile_img_url",
            "is_active",
            "updated_at",
        ]
