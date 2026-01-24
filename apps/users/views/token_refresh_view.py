from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers.token_refresh_serializer import TokenRefreshRequestSerializer


#JWT 토큰 재발급 API
class TokenRefreshAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="JWT 토큰 재발급 API",
        description="""
        refresh_token을 사용하여 새로운 access_token을 발급받습니다.
        access_token이 만료되었을 때 재로그인 없이 토큰을 갱신할 수 있습니다.
        """,
        request=TokenRefreshRequestSerializer,
        responses={
            200: OpenApiResponse(description="토큰 재발급 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            403: OpenApiResponse(description="유효하지 않은 토큰"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = TokenRefreshRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh_token = serializer.validated_data["refresh_token"]

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except (InvalidToken, TokenError):
            return Response(
                {"error_detail": {"detail": "로그인 세션이 만료되었습니다."}},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {"access_token": access_token},
            status=status.HTTP_200_OK,
        )
