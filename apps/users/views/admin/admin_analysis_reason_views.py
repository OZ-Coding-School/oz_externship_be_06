from typing import Any, List

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.withdrawal import Withdrawal
from apps.users.serializers.admin.admin_analysis_reason_serializers import (
    WithdrawalReasonStatsResponseSerializer,
)
from apps.users.services.admin_analysis_reason_service import AdminAnalysisReasonService


class WithdrawalReasonMonthlyStatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["admin_accounts"],
        summary="월별 탈퇴 사유 통계 조회",
        description="월별 탈퇴 사유 통계 데이터를 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="reason",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="탈퇴 사유 코드",
                enum=[choice[0] for choice in Withdrawal.Reason.choices],
            ),
        ],
        responses={200: WithdrawalReasonStatsResponseSerializer},
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        reason = request.query_params.get("reason")

        valid_reasons: List[str] = [choice[0] for choice in Withdrawal.Reason.choices]

        if not reason or reason not in valid_reasons:
            return Response(
                {"error_detail": f"유효하지 않은 사유입니다. 다음 중 하나를 선택하세요: {', '.join(valid_reasons)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AdminAnalysisReasonService()
        data = service.get_monthly_withdrawal_stats(reason)

        serializer = WithdrawalReasonStatsResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
