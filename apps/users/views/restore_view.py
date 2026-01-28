from datetime import date

from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.withdrawal import Withdrawal
from apps.users.serializers.restore_serializer import (
    RestoreErrorDetailSerializer,
    RestoreSerializer,
    RestoreSuccessSerializer,
)
from apps.users.utils.redis_utils import delete_email_token, get_email_by_token

User = get_user_model()


class RestoreAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="탈퇴 계정 복구 API",
        description="""
탈퇴 신청한 계정을 복구합니다. 유예 기간 내에만 복구 가능합니다.

## 플로우

1. `POST /api/v1/accounts/verification/send-email` - 탈퇴한 계정의 이메일로 인증 코드 발송
2. `POST /api/v1/accounts/verification/verify-email` - 인증 코드 확인 → `email_token` 반환
3. `POST /api/v1/accounts/restore` - 계정 복구 (현재 API)

## 복구 조건
- 탈퇴 신청 후 유예 기간(기본 30일) 내에만 복구 가능
- 유예 기간이 지나면 계정이 완전히 삭제되어 복구 불가

## 복구 후
- 계정이 활성화되어 정상 로그인 가능
- 기존 데이터(수강 기록 등)가 그대로 유지됨
        """,
        request=RestoreSerializer,
        responses={
            200: RestoreSuccessSerializer,
            404: RestoreErrorDetailSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = RestoreSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email_token = serializer.validated_data["email_token"]
        email = get_email_by_token(email_token)

        if not email:
            return Response({"error_detail": "유효하지 않은 인증 토큰입니다."}, status=status.HTTP_404_NOT_FOUND)

        withdrawal = Withdrawal.objects.select_related("user").filter(user__email=email).first()

        if not withdrawal:
            return Response(
                {"error_detail": "복구할 탈퇴 계정을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = withdrawal.user

        if user is None:
            return Response(
                {"error_detail": "복구할 계정을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if withdrawal.due_date < date.today():
            return Response(
                {"error_detail": "복구 가능 기간이 만료되었습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            user.is_active = True
            user.save(update_fields=["is_active"])
            withdrawal.delete()
            delete_email_token(email_token)

        return Response({"detail": "계정복구가 완료되었습니다."}, status=status.HTTP_200_OK)
