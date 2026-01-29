from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User, Withdrawal
from apps.users.serializers.login_serializer import LoginSerializer


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="이메일 로그인 API",
        description="""
이메일과 비밀번호로 로그인합니다.

## 응답
- 성공 시 `access_token`과 `refresh_token`이 반환됩니다.
- JWT 토큰을 사용하여 인증이 필요한 API 호출 시 헤더에 포함하세요.

## 토큰 유효기간
access token: 60분!
refresh token: 7일!
        """,
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="로그인 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            403: OpenApiResponse(description="탈퇴 신청한 계정"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user: User = serializer.validated_data["user"]

        # 탈퇴 신청한 계정인지 확인
        try:
            withdrawal = Withdrawal.objects.get(user=user)
            return Response(
                {
                    "error_detail": {
                        "detail": "탈퇴 신청한 계정입니다.",
                        "expire_at": withdrawal.due_date.strftime("%Y-%m-%d"),
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        except Withdrawal.DoesNotExist:
            pass

        result = serializer.save()

        return Response(result, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="로그아웃 API",
        description="""
현재 로그인된 사용자를 로그아웃합니다.

## 주의사항
- 인증 토큰이 필요합니다. (`Authorization: Bearer {access_token}`)
- 클라이언트에서 저장된 토큰을 삭제해야 완전한 로그아웃이 됩니다.
        """,
        responses={
            200: OpenApiResponse(description="로그아웃 성공"),
        },
    )
    def post(self, request: Request) -> Response:
        return Response({"detail": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)
