from typing import Any

from rest_framework import serializers

#카카오 프로필 검증
class KakaoProfileSerializer(serializers.Serializer[Any]):

    id = serializers.IntegerField()
    kakao_account = serializers.DictField(required=False, default=dict)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        kakao_account = attrs.get("kakao_account", {})
        email = kakao_account.get("email")

        if not email:
            raise serializers.ValidationError({"email": "카카오 계정에 이메일 정보가 필요합니다."})

        return attrs

#네이버 프로필 검증
class NaverProfileSerializer(serializers.Serializer[Any]):

    id = serializers.CharField()
    email = serializers.EmailField()
    nickname = serializers.CharField(required=False, allow_blank=True, default="")
    name = serializers.CharField(required=False, allow_blank=True, default="")
    profile_image = serializers.URLField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, default="")
    birthday = serializers.CharField(required=False, allow_blank=True, default="")
    birthyear = serializers.CharField(required=False, allow_blank=True, default="")
    mobile = serializers.CharField(required=False, allow_blank=True, default="")
