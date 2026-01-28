from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Withdrawal
from apps.users.serializers.withdrawal_serializer import (
    WithdrawalRequestSerializer,
    WithdrawalResponseSerializer,
)


class WithdrawalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="회원 탈퇴 요청",
        description="""
회원 탈퇴를 요청합니다.

## 탈퇴 처리 방식
- 탈퇴 요청 즉시 계정이 비활성화됩니다.
- 실제 데이터 삭제는 일정 기간(유예 기간) 후에 진행됩니다.
- 유예 기간 내에는 계정 복구가 가능합니다.

        """,
        request=WithdrawalRequestSerializer,
        responses={201: WithdrawalResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        user = request.user

        if not user.is_active:
            return Response(
                {"error_detail": "이미 탈퇴 처리된 계정입니다."},
                status=status.HTTP_409_CONFLICT,
            )

        existing = Withdrawal.objects.filter(user=user).first()
        if existing:
            return Response(
                {
                    "error_detail": "이미 탈퇴 신청한 계정입니다.",
                    "expire_at": existing.due_date,
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = WithdrawalRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            withdrawal = Withdrawal.objects.create(user=user, **serializer.validated_data)
            user.is_active = False
            user.save(update_fields=["is_active"])

        response_serializer = WithdrawalResponseSerializer(
            {
                "message": "회원 탈퇴 요청이 완료 되었습니다.",
                "due_date": withdrawal.due_date,
                "reason": withdrawal.reason,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
