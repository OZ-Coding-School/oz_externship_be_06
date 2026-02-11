import logging
import uuid

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
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

    @extend_schema(
        tags=["accounts"],
        summary="카카오 로그인 콜백",
        description="카카오 OAuth 콜백. 성공 시 access_token, refresh_token 반환.",
        responses={
            200: OpenApiResponse(description="로그인 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
        },
    )
    def get(self, request: Request) -> Response:
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

            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        except ValidationError as e:
            logger.warning("kakao callback validation error: %s", e.detail)
            return Response(
                {"error_detail": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except requests.exceptions.HTTPError:
            logger.exception("kakao callback oauth http error")
            return Response(
                {"error_detail": "카카오 인증 서버 오류"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("kakao callback unexpected error")
            return Response(
                {"error_detail": "로그인 처리 중 오류가 발생했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
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

    @extend_schema(
        tags=["accounts"],
        summary="네이버 로그인 콜백",
        description="네이버 OAuth 콜백. 성공 시 access_token, refresh_token 반환.",
        responses={
            200: OpenApiResponse(description="로그인 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
        },
    )
    def get(self, request: Request) -> Response:
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

            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        except ValidationError as e:
            logger.warning("naver callback validation error: %s", e.detail)
            return Response(
                {"error_detail": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except requests.exceptions.HTTPError:
            logger.exception("naver callback oauth http error")
            return Response(
                {"error_detail": "네이버 인증 서버 오류"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("naver callback unexpected error")
            return Response(
                {"error_detail": "로그인 처리 중 오류가 발생했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        finally:
            request.session.pop("oauth_state_naver", None)
