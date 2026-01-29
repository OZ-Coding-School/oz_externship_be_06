from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.users.models import User
from apps.users.utils.redis_utils import (
    delete_email_token,
    get_email_by_token,
)


def normalize_phone_number(phone: str) -> str:
    return phone.replace("-", "").strip()


class SignUpSerializer(serializers.ModelSerializer[User]):

    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    gender = serializers.ChoiceField(
        choices=[("M", "남성"), ("F", "여성")],
        required=True,
        error_messages={
            "required": "성별은 필수 항목입니다.",
            "invalid_choice": "올바른 성별을 선택해주세요. (M 또는 F)",
        },
    )
    email_token = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "이메일 인증 토큰은 필수 항목입니다."},
    )
    sms_token = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "SMS 인증 토큰은 필수 항목입니다."},
    )

    class Meta:
        model = User
        fields = [
            "password",
            "password_confirm",
            "nickname",
            "name",
            "birthday",
            "gender",
            "email_token",
            "sms_token",
        ]

    def validate_nickname(self, value: str) -> str:
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def validate_email_token(self, value: str) -> str:
        if not get_email_by_token(value):
            raise serializers.ValidationError("유효하지 않거나 만료된 이메일 인증 토큰입니다.")
        return value

    def validate_sms_token(self, value: str) -> str:
        if not cache.get(f"sms_verified:{value}"):
            raise serializers.ValidationError("유효하지 않거나 만료된 SMS 인증 토큰입니다.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # 비밀번호 확인
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})

        # 비밀번호 유효성 검사
        try:
            validate_password(password)
        except ValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        # 토큰에서 email, phone_number 추출
        email_token: str = attrs["email_token"]
        sms_token: str = attrs["sms_token"]

        email = get_email_by_token(email_token)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email_token": "이미 가입된 이메일입니다."})

        attrs["email"] = email

        # SMS 토큰에서 phone_number 추출
        phone_number = cache.get(f"sms_verified:{sms_token}")
        phone_number = normalize_phone_number(phone_number)

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"sms_token": "이미 가입된 휴대폰 번호입니다."})

        attrs["phone_number"] = phone_number

        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        # 토큰 제거
        email_token = validated_data.pop("email_token")
        sms_token = validated_data.pop("sms_token")

        gender_map = {"M": User.Gender.MALE, "F": User.Gender.FEMALE}
        validated_data["gender"] = gender_map[validated_data["gender"]]

        # 비밀번호 추출
        password = validated_data.pop("password")

        # 유저 생성 (인증 완료했으므로 is_active=True)
        user = User.objects.create_user(
            email=validated_data.pop("email"),
            password=password,
            is_active=True,
            **validated_data,
        )

        # 인증 토큰 캐시 삭제
        delete_email_token(email_token)
        cache.delete(f"sms_verified:{sms_token}")

        return user


class SignupNicknameCheckSerializer(serializers.Serializer[dict[str, Any]]):

    nickname = serializers.CharField(
        max_length=10,
        required=True,
        error_messages={
            "required": "이 필드는 필수 항목입니다.",
            "blank": "닉네임을 입력해주세요.",
            "max_length": "닉네임은 10자 이하로 입력해주세요.",
        },
    )
