from __future__ import annotations

import secrets

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client  # type: ignore[import-untyped]

from apps.users.serializers.sms_verification_serializer import (
    SendSmsVerificationSerializer,
    VerifySmsSerializer,
)
from apps.users.utils.redis_utils import save_sms_token


def get_twilio_client() -> Client:
    """Twilio 클라이언트 생성."""
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def generate_sms_token() -> str:
    """SMS 인증 토큰 생성."""
    return secrets.token_urlsafe(24)


class SendSmsVerificationAPIView(APIView):
    """SMS 인증 코드 발송 API (Twilio Verify)."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="통합 SMS 인증 발송 API",
        description="""
        휴대폰 번호로 6자리 인증 코드를 발송합니다.
        회원가입, 휴대폰 번호 변경 등에서 사용됩니다.
        인증 코드는 10분간 유효합니다.
        """,
        request=SendSmsVerificationSerializer,
        responses={
            200: OpenApiResponse(description="SMS 인증 코드 발송 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SendSmsVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone_number = serializer.validated_data["phone_number"]

        try:
            client = get_twilio_client()
            client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                to=f"+82{phone_number[1:]}",
                channel="sms",
            )
        except Exception:
            return Response(
                {"error_detail": "SMS 발송에 실패했습니다. 잠시 후 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"detail": "회원가입을 위한 휴대폰 인증 코드가 전송되었습니다."},
            status=status.HTTP_200_OK,
        )


class VerifySmsAPIView(APIView):
    """SMS 인증 코드 확인 API (Twilio Verify)."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="통합 SMS 인증 API",
        description="""
        휴대폰으로 발송된 인증 코드를 검증합니다.
        인증 성공 시 회원가입에 사용할 sms_token을 반환합니다.
        sms_token은 1시간 동안 유효합니다.
        """,
        request=VerifySmsSerializer,
        responses={
            200: OpenApiResponse(description="SMS 인증 성공"),
            400: OpenApiResponse(description="인증 코드 불일치"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = VerifySmsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        try:
            client = get_twilio_client()
            verification_check = client.verify.v2.services(
                settings.TWILIO_VERIFY_SERVICE_SID
            ).verification_checks.create(
                to=f"+82{phone_number[1:]}",
                code=code,
            )
        except Exception:
            return Response(
                {"error_detail": {"code": ["인증 처리 중 오류가 발생했습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if verification_check.status != "approved":
            return Response(
                {"error_detail": {"code": ["인증 코드가 일치하지 않습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # sms_token 생성 및 저장 (1시간 유효)
        sms_token = generate_sms_token()
        save_sms_token(sms_token, phone_number)

        return Response(
            {
                "detail": "회원가입을 위한 휴대폰 인증에 성공하였습니다.",
                "sms_token": sms_token,
            },
            status=status.HTTP_200_OK,
        )
