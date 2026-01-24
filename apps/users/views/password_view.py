from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.password_serializer import (
    ChangePasswordSerializer,
    FindPasswordSerializer,
)
from apps.users.utils.redis_utils import delete_email_token, get_email_by_token

#비밀번호 변경 API (로그인 상태)
class ChangePasswordAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="비밀번호 재설정 API",
        description="""
        로그인한 사용자가 비밀번호를 변경합니다.
        기존 비밀번호(old_password)를 확인한 후 새 비밀번호(new_password)로 변경합니다.
        """,
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="비밀번호 변경 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            401: OpenApiResponse(description="인증 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user: User = request.user  # type: ignore[assignment]
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # 기존 비밀번호 확인
        if not user.check_password(old_password):
            return Response(
                {"error_detail": {"old_password": ["기존 비밀번호가 일치하지 않습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새 비밀번호 설정
        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {"detail": "비밀번호 변경 성공."},
            status=status.HTTP_200_OK,
        )

#비밀번호 분실 시 재설정
class FindPasswordAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="비밀번호 분실 시 재설정 API",
        description="""
        이메일 인증 후 발급받은 email_token을 사용하여 비밀번호를 재설정합니다.
        로그인하지 않은 상태에서 비밀번호를 분실한 경우 사용합니다.
        """,
        request=FindPasswordSerializer,
        responses={
            200: OpenApiResponse(description="비밀번호 변경 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = FindPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_token = serializer.validated_data["email_token"]
        new_password = serializer.validated_data["new_password"]

        # email_token으로 이메일 조회
        email = get_email_by_token(email_token)

        if not email:
            return Response(
                {"error_detail": {"email_token": ["유효하지 않거나 만료된 토큰입니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 사용자 조회
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error_detail": {"email_token": ["해당 이메일로 가입된 사용자가 없습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새 비밀번호 설정
        user.set_password(new_password)
        user.save(update_fields=["password"])

        # email_token 삭제 (1회용)
        delete_email_token(email_token)

        return Response(
            {"detail": "비밀번호 변경 성공."},
            status=status.HTTP_200_OK,
        )
