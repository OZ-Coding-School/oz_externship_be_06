from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.sign_up_serializer import (
    SignupNicknameCheckSerializer,
    SignUpSerializer,
)


# 회원가입api
class SignUpAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="회원가입 API",
        description="""
        회원가입을 진행합니다.
        이메일 인증과 SMS 인증이 완료된 토큰이 필요
        """,
        request=SignUpSerializer,
        responses={
            201: OpenApiResponse(description="회원가입 성공"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            409: OpenApiResponse(description="중복된 회원가입 내역"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SignUpSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()
        except Exception:
            return Response(
                {"error_detail": "이미 중복된 회원가입 내역이 존재합니다."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"detail": "회원가입이 완료되었습니다."},
            status=status.HTTP_201_CREATED,
        )


# 닉네임 중복 확인 api
class SignupNicknameCheckAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="닉네임 중복 확인 API",
        description="닉네임 중복 여부를 확인합니다.",
        request=SignupNicknameCheckSerializer,
        responses={
            200: OpenApiResponse(description="사용 가능한 닉네임"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            409: OpenApiResponse(description="중복된 닉네임"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SignupNicknameCheckSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nickname = serializer.validated_data["nickname"]

        if User.objects.filter(nickname=nickname).exists():
            return Response(
                {"error_detail": "이미 사용중인 닉네임 입니다"},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"detail": "사용가능한 닉네임 입니다."},
            status=status.HTTP_200_OK,
        )
