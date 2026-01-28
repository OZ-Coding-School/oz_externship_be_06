import secrets
import uuid

from django.conf import settings
from django.core.mail import send_mail
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.base62 import Base62
from apps.users.serializers.email_verification_serializer import (
    SendEmailVerificationSerializer,
    VerifyEmailSerializer,
)
from apps.users.utils.redis_utils import (
    delete_email_code,
    get_email_code,
    save_email_code,
    save_email_token,
)


def generate_verification_code() -> str:
    return Base62.uuid_encode(uuid.uuid4(), length=6)


def generate_email_token() -> str:
    return secrets.token_urlsafe(24)  # 24 bytes → 32 characters


# 이메일 발송 api
class SendEmailVerificationAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="통합 이메일 인증 발송 API",
        description="""
이메일로 6자리 인증 코드를 발송합니다.

## 사용 목적
- 회원가입 시 이메일 인증
- 비밀번호 찾기
- 탈퇴 계정 복구

## 동작 방식
1. 이메일 주소로 6자리 인증 코드 발송
2. Redis에 인증 코드 저장 (5분간 유효)
3. 동일 이메일로 재요청 시 기존 코드가 덮어쓰기됨

        """,
        request=SendEmailVerificationSerializer,
        responses={
            200: OpenApiResponse(description="이메일 인증 코드 발송 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SendEmailVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        code = generate_verification_code()

        # Redis에 인증 코드 저장 (5분 유효)
        save_email_code(email, code)

        # 이메일 발송
        try:
            send_mail(
                subject="[오즈코딩스쿨] 이메일 인증 코드",
                message=f"인증 코드: {code}\n\n이 코드는 5분간 유효합니다.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            return Response(
                {"error_detail": "이메일 발송에 실패했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"detail": "이메일 인증 코드가 전송되었습니다."},
            status=status.HTTP_200_OK,
        )


# 이메일 인증 api
class VerifyEmailAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="통합 이메일 인증 API",
        description="""
이메일로 발송된 인증 코드를 검증합니다.

## 요청 필드
- `email`: 인증 코드를 받은 이메일 주소
- `code`: 6자리 인증 코드

## 응답
- 인증 성공 시 `email_token` 반환
- `email_token`은 1시간 동안 유효합니다.

## 사용 용도별 다음 단계
- **회원가입**: `POST /api/v1/accounts/signup` 요청 시 `email_token` 필드에 포함
- **비밀번호 찾기**: `POST /api/v1/accounts/find-password` 요청 시 `email_token` 필드에 포함
- **계정 복구**: `POST /api/v1/accounts/restore` 요청 시 `email_token` 필드에 포함

## 에러 케이스
- **400**: 인증 코드가 만료됨 (5분 초과)
- **400**: 인증 코드가 일치하지 않음
        """,
        request=VerifyEmailSerializer,
        responses={
            200: OpenApiResponse(description="이메일 인증 성공"),
            400: OpenApiResponse(description="인증 코드 불일치"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = VerifyEmailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        # Redis에서 인증 코드 조회
        stored_code = get_email_code(email)

        if not stored_code:
            return Response(
                {"error_detail": {"code": ["인증 코드가 만료되었거나 존재하지 않습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if stored_code != code:
            return Response(
                {"error_detail": {"code": ["인증 코드가 일치하지 않습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 인증 코드 삭제
        delete_email_code(email)

        # email_token 생성 및 저장 (1시간 유효)
        email_token = generate_email_token()
        save_email_token(email_token, email)

        return Response(
            {
                "detail": "이메일 인증에 성공하였습니다.",
                "email_token": email_token,
            },
            status=status.HTTP_200_OK,
        )
