from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.withdrawal_serializer import WithdrawalRequestSerializer
from apps.users.services.withdrawal_service import withdraw_user


class WithdrawalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="회원 탈퇴 API",
        description="""
회원 탈퇴를 신청합니다.

## 요청 필드
- `reason`: 탈퇴 사유 (선택지)
- `reason_detail`: 탈퇴 상세 사유
        """,
        request=WithdrawalRequestSerializer,
        responses={
            204: OpenApiResponse(description="탈퇴 신청 성공"),
            400: OpenApiResponse(description="유효성 검사 실패 또는 이미 탈퇴 신청한 계정"),
            401: OpenApiResponse(description="인증되지 않은 사용자"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = WithdrawalRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        assert isinstance(request.user, User)
        withdraw_user(user=request.user, reason=data["reason"], reason_detail=data["reason_detail"])
        return Response(status=status.HTTP_204_NO_CONTENT)
