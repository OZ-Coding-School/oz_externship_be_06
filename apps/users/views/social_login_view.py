import logging
import uuid
from typing import Literal, cast
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Withdrawal
from apps.users.serializers.social_serializer import (
    KakaoProfileSerializer,
    NaverProfileSerializer,
)
from apps.users.utils.social_login import (
    KakaoOAuthService,
    NaverOAuthService,
)

logger = logging.getLogger(__name__)


# 프론트엔드 리다이렉트
def frontend_redirect(*, provider: str, is_success: bool = True) -> HttpResponseRedirect:
    base = getattr(settings, "FRONTEND_SOCIAL_REDIRECT_URL", "") or "/"
    params = {"provider": provider, "is_success": str(is_success).lower()}
    return redirect(f"{base}?{urlencode(params)}")


# 인증토큰을 쿠키에 설정
def set_auth_cookies(resp: HttpResponseRedirect, *, access: str, refresh: str) -> None:
    secure = getattr(settings, "SESSION_COOKIE_SECURE", False)
    samesite = cast(
        Literal["Lax", "Strict", "None", False] | None,
        getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
    )
    cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)

    resp.set_cookie(
        "access_token",
        access,
        domain=cookie_domain,
        httponly=False,
        secure=secure,
        samesite=samesite,
        path="/",
    )

    resp.set_cookie(
        "refresh_token",
        refresh,
        domain=cookie_domain,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )


# 카카오로그인
class KakaoLoginStartAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="카카오 로그인 시작",
        description="카카오 OAuth 인증 페이지로 리다이렉트",
        responses={302: None},
    )
    def get(self, request: Request) -> HttpResponseRedirect:
        state = uuid.uuid4().hex
        request.session["oauth_state_kakao"] = state

        authorize_url = (
            f"{KakaoOAuthService.AUTHORIZE_URL}"
            f"?response_type=code"
            f"&client_id={settings.KAKAO_CLIENT_ID}"
            f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
            f"&state={state}"
        )
        return redirect(authorize_url)


# 카카오 로그인 콜백
class KakaoCallbackAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, request: Request) -> HttpResponseRedirect:
        try:
            code = request.query_params.get("code")
            state = request.query_params.get("state")

            # code, state 유무 검증
            if not code or not state:
                raise ValidationError({"code": "code_state_required"})

            # state 검증 (CSRF 방지)
            if state != request.session.get("oauth_state_kakao"):
                raise ValidationError({"code": "invalid_state"})

            service = KakaoOAuthService()
            access_token = service.get_access_token(code)
            profile = service.get_user_info(access_token)

            # 프로필 검증
            serializer = KakaoProfileSerializer(data=profile)
            serializer.is_valid(raise_exception=True)

            # 유저 조회 또는 생성
            user = service.get_or_create_user(profile)

            # 비활성화 유저 검증
            if not user.is_active:
                raise ValidationError({"code": "inactive_user"})

            # 탈퇴 신청한 계정 검증
            if Withdrawal.objects.filter(user=user).exists():
                raise ValidationError({"code": "withdrawn_user"})

            # JWT 토큰 발급
            refresh = RefreshToken.for_user(user)

            resp = frontend_redirect(provider="kakao")
            set_auth_cookies(resp, access=str(refresh.access_token), refresh=str(refresh))
            return resp

        except ValidationError as e:
            logger.warning("kakao callback validation error: %s", e.detail)
            return frontend_redirect(provider="kakao", is_success=False)
        except requests.exceptions.HTTPError:
            logger.exception("kakao callback oauth http error")
            return frontend_redirect(provider="kakao", is_success=False)
        except Exception:
            logger.exception("kakao callback unexpected error")
            return frontend_redirect(provider="kakao", is_success=False)
        finally:
            request.session.pop("oauth_state_kakao", None)


# 네이버 로그인
class NaverLoginStartAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="네이버 로그인 시작",
        description="네이버 OAuth 인증 페이지로 리다이렉트",
        responses={302: None},
    )
    def get(self, request: Request) -> HttpResponseRedirect:
        state = uuid.uuid4().hex
        request.session["oauth_state_naver"] = state

        authorize_url = (
            f"{NaverOAuthService.AUTHORIZE_URL}"
            f"?response_type=code"
            f"&client_id={settings.NAVER_CLIENT_ID}"
            f"&redirect_uri={settings.NAVER_REDIRECT_URI}"
            f"&state={state}"
        )
        return redirect(authorize_url)


# 네이버 로그인 콜백
class NaverCallbackAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(exclude=True)
    def get(self, request: Request) -> HttpResponseRedirect:
        try:
            code = request.query_params.get("code")
            state = request.query_params.get("state")

            # code, state 유무 검증
            if not code or not state:
                raise ValidationError({"code": "code_state_required"})

            # state 검증 (CSRF 방지)
            if state != request.session.get("oauth_state_naver"):
                raise ValidationError({"code": "invalid_state"})

            service = NaverOAuthService()
            access_token = service.get_access_token(code, state)
            profile = service.get_user_info(access_token)

            # 프로필 검증
            serializer = NaverProfileSerializer(data=profile)
            serializer.is_valid(raise_exception=True)

            # 유저 조회 또는 생성
            user = service.get_or_create_user(serializer.validated_data)

            # 비활성화 유저 검증
            if not user.is_active:
                raise ValidationError({"code": "inactive_user"})

            # 탈퇴 신청한 계정 검증
            if Withdrawal.objects.filter(user=user).exists():
                raise ValidationError({"code": "withdrawn_user"})

            # JWT 토큰 발급
            refresh = RefreshToken.for_user(user)

            resp = frontend_redirect(provider="naver")
            set_auth_cookies(resp, access=str(refresh.access_token), refresh=str(refresh))
            return resp

        except ValidationError as e:
            logger.warning("naver callback validation error: %s", e.detail)
            return frontend_redirect(provider="naver", is_success=False)
        except requests.exceptions.HTTPError:
            logger.exception("naver callback oauth http error")
            return frontend_redirect(provider="naver", is_success=False)
        except Exception:
            logger.exception("naver callback unexpected error")
            return frontend_redirect(provider="naver", is_success=False)
        finally:
            request.session.pop("oauth_state_naver", None)
