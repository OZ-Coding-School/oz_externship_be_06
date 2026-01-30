from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers.token_refresh_serializer import (
    TokenRefreshRequestSerializer,
)


# JWT 토큰 재발급 API
class TokenRefreshAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="JWT 토큰 재발급 API",
        description="""
`refresh_token`을 사용하여 새로운 `access_token`을 발급받습니다.


        """,
        request=TokenRefreshRequestSerializer,
        responses={
            200: OpenApiResponse(description="토큰 재발급 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            403: OpenApiResponse(description="유효하지 않은 토큰"),
        },
    )
    def post(self, request: Request) -> Response:
        # 쿠키에서 refresh_token 먼저 확인, 없으면 body에서 확인
        refresh_token = request.COOKIES.get("refresh_token")
        from_cookie = bool(refresh_token)

        if not refresh_token:
            serializer = TokenRefreshRequestSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    {"error_detail": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh_token = str(serializer.validated_data["refresh_token"])

        try:
            refresh = RefreshToken(refresh_token)  # type: ignore[arg-type]
            access_token = str(refresh.access_token)
        except (InvalidToken, TokenError):
            return Response(
                {"error_detail": {"detail": "로그인 세션이 만료되었습니다."}},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = Response(
            {"access_token": access_token},
            status=status.HTTP_200_OK,
        )

        # 소셜 로그인 사용자용: 쿠키로 refresh_token을 받은 경우 access_token도 쿠키로 갱신
        if from_cookie:
            cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)
            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=60 * 60,  # 60분
                domain=cookie_domain,
                httponly=False,
                secure=not settings.DEBUG,
                samesite="Lax",
            )

        return response
