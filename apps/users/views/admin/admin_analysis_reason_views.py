from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
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
    """
    어드민용 월별 탈퇴 사유 통계 뷰
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["admin_accounts"],
        summary="월별 탈퇴 사유 통계 조회",
        description="관리자가 특정 탈퇴 사유에 대한 월별 통계 데이터를 조회합니다.",
        parameters=[WithdrawalReasonStatsRequestSerializer],
        responses={
            200: WithdrawalReasonStatsResponseSerializer,
            400: OpenApiResponse(description="잘못된 요청 데이터 (사유 누락 또는 유효하지 않은 사유)"),
            401: OpenApiResponse(description="인증되지 않은 사용자"),
            403: OpenApiResponse(description="관리자 권한 없음"),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        탈퇴 사유별 월별 통계 리스트를 반환합니다.
        """
        # 1. 요청 데이터 검증
        # context를 넘겨 시리얼라이저 내부에서 필요한 정보에 접근 가능하게 합니다.
        query_serializer = WithdrawalReasonStatsRequestSerializer(
            data=request.query_params, context={"request": request}
        )

        # 테스트 코드의 요구사항(error_detail 키 확인)에 맞춰 커스텀 에러 응답 처리
        if not query_serializer.is_valid():
            return Response(
                {"error_detail": query_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = query_serializer.validated_data["reason"]

        # 2. 비즈니스 로직 수행
        service = AdminAnalysisReasonService()
        data = service.get_monthly_withdrawal_stats(reason)

        # 3. 응답 직렬화 및 반환
        response_serializer = WithdrawalReasonStatsResponseSerializer(data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
