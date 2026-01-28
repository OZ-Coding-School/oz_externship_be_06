from typing import Any

from rest_framework import serializers

from apps.users.models import User

# 어드민 회원 정보 수정
class AdminAccountUpdateRequestSerializer(serializers.Serializer[Any]):

    nickname = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=30, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    birthday = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=User.Gender.choices, required=False)
    profile_img_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    def validate_phone_number(self, value: str) -> str:
        if value and not value.isdigit():
            raise serializers.ValidationError("전화번호는 숫자만 입력 가능합니다.")
        if value and len(value) != 11:
            raise serializers.ValidationError("11자리 숫자로 구성된 포맷이어야 합니다.")
        return value

    def validate_nickname(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("닉네임은 빈 값일 수 없습니다.")
        return value.strip()

    def validate_name(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("이름은 빈 값일 수 없습니다.")
        return value.strip()

#어드민 회원 정보 수정 응답
class AdminAccountUpdateResponseSerializer(serializers.ModelSerializer[User]):

    gender = serializers.CharField(source="get_gender_display")

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
