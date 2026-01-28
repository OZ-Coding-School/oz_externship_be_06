import logging
from datetime import date
from typing import Any

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.users.models.social_user import SocialUser

logger = logging.getLogger(__name__)

User = get_user_model()


def parse_kakao_birthday(kakao_account: dict[str, Any]) -> date | None:
    birthday = kakao_account.get("birthday")

    if not (birthday and len(birthday) == 4):
        return None

    try:
        month = int(birthday[:2])
        day = int(birthday[2:])
        year = 2000  # 기본 연도
        return date(year, month, day)
    except ValueError:
        return None


def parse_naver_birthday(naver_profile: dict[str, Any]) -> date | None:
    birthyear = naver_profile.get("birthyear")
    birthday = naver_profile.get("birthday")

    if not (birthyear and birthday):
        return None

    try:
        year = int(birthyear)
        month = int(birthday[:2])
        day = int(birthday[3:])
        return date(year, month, day)
    except ValueError:
        return None


class KakaoOAuthService:

    AUTHORIZE_URL = "https://kauth.kakao.com/oauth/authorize"
    TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

    def get_access_token(self, code: str) -> str:
        # 인가 코드로 access_token 발급
        response = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code,
            },
            timeout=10,
        )
        response.raise_for_status()
        token: str = response.json()["access_token"]
        return token

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        # access_token으로 사용자 정보 조회
        response = requests.get(
            self.USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data

    def get_or_create_user(self, profile: dict[str, Any]) -> Any:
        # 카카오톡 프로필 유저 조회
        kakao_id = str(profile.get("id"))
        kakao_account = profile.get("kakao_account", {})
        kakao_profile = kakao_account.get("profile", {})

        email = kakao_account.get("email")
        nickname = kakao_profile.get("nickname", "")
        profile_image = kakao_profile.get("profile_image_url") or kakao_profile.get("thumbnail_image_url")
        gender = kakao_account.get("gender")  # 남자여자
        birthday_date = parse_kakao_birthday(kakao_account)

        if not email:
            raise ValidationError({"code": "email_required", "message": "카카오 계정에 이메일이 없습니다."})

        # 기존 소셜 유저 조회
        social_user = (
            SocialUser.objects.filter(
                provider=SocialUser.Provider.KAKAO,
                provider_id=kakao_id,
            )
            .select_related("user")
            .first()
        )

        if social_user:
            return social_user.user

        # 이메일로 기존 유저 조회
        user = User.objects.filter(email__iexact=email).first()

        if user:
            # 기존 유저에 소셜 연결
            SocialUser.objects.get_or_create(
                user=user,
                provider=SocialUser.Provider.KAKAO,
                provider_id=kakao_id,
            )
            return user

        # 성별 처리
        user_gender = User.Gender.MALE
        if gender == "female":
            user_gender = User.Gender.FEMALE

        # 생년월일 처리
        full_birthday = birthday_date if birthday_date else date(1990, 1, 1)

        with transaction.atomic():
            # 신규 유저 생성
            user = User.objects.create_user(
                email=email,
                nickname=nickname[:10] if nickname else f"kakao_{kakao_id[:4]}",
                name=nickname[:30] if nickname else "카카오유저",
                phone_number="",
                gender=user_gender,
                birthday=full_birthday,
                profile_img_url=profile_image,
                is_active=True,
            )

            # 소셜 유저 연결
            SocialUser.objects.create(
                user=user,
                provider=SocialUser.Provider.KAKAO,
                provider_id=kakao_id,
            )

        return user


class NaverOAuthService:

    AUTHORIZE_URL = "https://nid.naver.com/oauth2.0/authorize"
    TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"

    def get_access_token(self, code: str, state: str) -> str:
        # 인가 코드로 access_token 발급
        response = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.NAVER_CLIENT_ID,
                "client_secret": settings.NAVER_CLIENT_SECRET,
                "code": code,
                "state": state,
            },
            timeout=10,
        )
        response.raise_for_status()
        token: str = response.json()["access_token"]
        return token

    def get_user_info(self, access_token: str) -> dict[str, Any]:
        # access_token으로 사용자 정보 조회
        response = requests.get(
            self.USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        profile: dict[str, Any] | None = data.get("response")
        if not profile:
            raise ValidationError({"code": "naver_api_error", "message": "네이버 프로필 응답이 비어있습니다."})

        return profile

    def get_or_create_user(self, profile: dict[str, Any]) -> Any:
        # 네이버 프로필로 유저 조회 또는 생성
        naver_id = str(profile.get("id"))
        email = profile.get("email")
        nickname = profile.get("nickname", "")
        name = profile.get("name", "")
        profile_image = profile.get("profile_image")
        gender = profile.get("gender")  # M or F
        birthday_date = parse_naver_birthday(profile)
        mobile = profile.get("mobile", "").replace("-", "")

        if not email:
            raise ValidationError({"code": "email_required", "message": "네이버 계정에 이메일이 없습니다."})

        # 기존 소셜 유저 조회
        social_user = (
            SocialUser.objects.filter(
                provider=SocialUser.Provider.NAVER,
                provider_id=naver_id,
            )
            .select_related("user")
            .first()
        )

        if social_user:
            return social_user.user

        # 이메일로 기존 유저 조회
        user = User.objects.filter(email__iexact=email).first()

        if user:
            # 기존 유저에 소셜 연결
            SocialUser.objects.get_or_create(
                user=user,
                provider=SocialUser.Provider.NAVER,
                provider_id=naver_id,
            )
            return user

        # 성별 처리
        user_gender = User.Gender.MALE
        if gender == "F":
            user_gender = User.Gender.FEMALE

        # 생년월일 처리
        full_birthday = birthday_date if birthday_date else date(1990, 1, 1)

        with transaction.atomic():
            # 신규 유저 생성
            user = User.objects.create_user(
                email=email,
                nickname=nickname[:10] if nickname else f"naver_{naver_id[:4]}",
                name=name[:30] if name else "네이버유저",
                phone_number=mobile,
                gender=user_gender,
                birthday=full_birthday,
                profile_img_url=profile_image,
                is_active=True,
            )

            # 소셜 유저 연결
            SocialUser.objects.create(
                user=user,
                provider=SocialUser.Provider.NAVER,
                provider_id=naver_id,
            )

        return user
