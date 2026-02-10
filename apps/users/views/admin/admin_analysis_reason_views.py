from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.admin.admin_analysis_reason_serializers import (
    WithdrawalReasonStatsRequestSerializer,
    WithdrawalReasonStatsResponseSerializer,
)
from apps.users.services.admin_analysis_reason_service import AdminAnalysisReasonService


class WithdrawalReasonMonthlyStatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["admin_accounts"],
        summary="월별 탈퇴 사유 통계 조회",
        description="월별 탈퇴 사유 통계 데이터를 조회합니다.",
        parameters=[WithdrawalReasonStatsRequestSerializer],  # 시리얼라이저로 파라미터 자동 정의
        responses={200: WithdrawalReasonStatsResponseSerializer},
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 1. 요청 데이터 검증 (Serializer 활용)
        query_serializer = WithdrawalReasonStatsRequestSerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        reason = query_serializer.validated_data["reason"]

        # 2. 비즈니스 로직 수행 (Service 호출)
        service = AdminAnalysisReasonService()
        data = service.get_monthly_withdrawal_stats(reason)

        # 3. 응답 반환
        response_serializer = WithdrawalReasonStatsResponseSerializer(data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
