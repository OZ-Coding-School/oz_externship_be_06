from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.users.services.admin_analysis_reason_service import AdminAnalysisReasonService
from apps.users.serializers.admin.admin_analysis_reason_serializers import WithdrawalReasonStatsResponseSerializer
from apps.users.models.withdrawal import Withdrawal

class WithdrawalReasonMonthlyStatsView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="월별 탈퇴 사유 통계 데이터를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'reason',
                openapi.IN_QUERY,
                description="탈퇴 사유 코드",
                type=openapi.TYPE_STRING,
                required=True,
                # 모델에 정의된 실제 Choice 값들로 수정
                enum=[choice[0] for choice in Withdrawal.Reason.choices]
            )
        ],
        responses={200: WithdrawalReasonStatsResponseSerializer},
        tags=['Admin Analytics']
    )
    def get(self, request):
        reason = request.query_params.get('reason')

        # 모델에 정의된 유효한 사유인지 검증
        valid_reasons = [choice[0] for choice in Withdrawal.Reason.choices]
        if not reason or reason not in valid_reasons:
            return Response(
                {"error_detail": f"유효하지 않은 사유입니다. 다음 중 하나를 선택하세요: {', '.join(valid_reasons)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = AdminAnalysisReasonService()
        data = service.get_monthly_withdrawal_stats(reason)

        serializer = WithdrawalReasonStatsResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)