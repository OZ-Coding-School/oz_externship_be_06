from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken


# JWT 토큰 재발급 API
class TokenRefreshAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="JWT 토큰 재발급 API",
        description="쿠키의 `refresh_token`을 사용하여 새로운 `access_token`을 발급받습니다.",
        responses={
            200: OpenApiResponse(description="토큰 재발급 성공"),
            400: OpenApiResponse(description="refresh_token 쿠키 없음"),
            403: OpenApiResponse(description="유효하지 않은 토큰"),
        },
    )
    def post(self, request: Request) -> Response:
        # 쿠키에서 refresh_token 확인
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error_detail": "refresh_token 쿠키가 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)  # type: ignore[arg-type]
            access_token = str(refresh.access_token)
        except (InvalidToken, TokenError):
            return Response(
                {"error_detail": "로그인 세션이 만료되었습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = Response(
            {"access_token": access_token},
            status=status.HTTP_200_OK,
        )

        # access_token을 쿠키에도 저장
        cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60,  # 60분
            domain=cookie_domain,
            httponly=False,
            secure=settings.COOKIE_SECURE,
            samesite="None" if settings.COOKIE_SECURE else "Lax",
        )

        return response
