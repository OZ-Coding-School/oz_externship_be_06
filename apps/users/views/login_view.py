from django.conf import settings
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
- 성공 시 `access_token`이 반환됩니다.

## 토큰 유효기간
access token: 60분
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

        # 탈퇴 신청한 계정인지 비활성화된 계정인지 확인
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
            # Withdrawal 레코드 없이 비활성화된 계정
            if not user.is_active:
                return Response(
                    {
                        "error_detail": {
                            "detail": "비활성화된 계정입니다.",
                            "expire_at": None,
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        result = serializer.save()

        # access_token만 body로 반환, refresh_token은 httpOnly 쿠키로 설정
        response = Response(
            {"access_token": result["access_token"]},
            status=status.HTTP_200_OK,
        )

        # refresh_token을 httpOnly 쿠키로 설정
        cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            max_age=7 * 24 * 60 * 60,  # 7일
            domain=cookie_domain,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="None" if settings.COOKIE_SECURE else "Lax",
            path="/",
        )

        return response


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="로그아웃 API",
        description="""
현재 로그인된 사용자를 로그아웃합니다.

## 주의사항
- 인증 토큰이 필요합니다. (`Authorization: Bearer {access_token}`)
        """,
        responses={
            200: OpenApiResponse(description="로그아웃 성공"),
        },
    )
    def post(self, request: Request) -> Response:
        response = Response({"detail": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")  # 토큰 재발급 시 설정된 쿠키 삭제
        return response
