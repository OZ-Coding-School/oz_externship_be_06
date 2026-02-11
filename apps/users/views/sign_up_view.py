from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.sign_up_serializer import (
    SignupEmailCheckSerializer,
    SignupNicknameCheckSerializer,
    SignupPhoneCheckSerializer,
    SignUpSerializer,
    normalize_phone_number,
)


# 회원가입api
class SignUpAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="회원가입 API",
        description="""
신규 회원가입을 진행합니다.

## 사전 조건
회원가입 전에 아래 인증 절차를 완료해야 합니다:

1. **이메일 인증**
   - `POST /api/v1/accounts/verification/send-email` - 인증 코드 발송
   - `POST /api/v1/accounts/verification/verify-email` - 인증 코드 확인 → `email_token` 반환

2. **SMS 인증**
   - `POST /api/v1/accounts/verification/send-sms` - 인증 코드 발송
   - `POST /api/v1/accounts/verification/verify-sms` - 인증 코드 확인 → `sms_token` 반환

3. **닉네임 중복 확인**
   - `POST /api/v1/accounts/signup/check-nickname` - 닉네임 사용 가능 여부 확인

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


# 중복 확인 베이스 클래스
class BaseDuplicateCheckAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class: type
    field_name: str
    error_message: str
    success_message: str

    def get_check_value(self, validated_data: dict) -> str:
        return validated_data[self.field_name]

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        value = self.get_check_value(serializer.validated_data)

        if User.objects.filter(**{self.field_name: value}).exists():
            return Response(
                {"error_detail": self.error_message},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"detail": self.success_message},
            status=status.HTTP_200_OK,
        )


# 닉네임 중복 확인 api
class SignupNicknameCheckAPIView(BaseDuplicateCheckAPIView):
    serializer_class = SignupNicknameCheckSerializer
    field_name = "nickname"
    error_message = "이미 사용중인 닉네임 입니다"
    success_message = "사용가능한 닉네임 입니다."

    @extend_schema(
        tags=["accounts"],
        summary="닉네임 중복 확인 API",
        description="""
회원가입 시 사용할 닉네임의 중복 여부를 확인합니다.

## 요청 필드
- `nickname`: 확인할 닉네임 (최대 10자)

## 응답
- **200**: 사용 가능한 닉네임
- **409**: 이미 사용 중인 닉네임

## 주의사항
- 회원가입 전에 반드시 닉네임 중복 확인을 해주세요.
- 특수문자 사용 제한이 있을 수 있습니다.
        """,
        request=SignupNicknameCheckSerializer,
        responses={
            200: OpenApiResponse(description="사용 가능한 닉네임"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            409: OpenApiResponse(description="중복된 닉네임"),
        },
    )
    def post(self, request: Request) -> Response:
        return super().post(request)


# 이메일 중복 확인 api
class SignupEmailCheckAPIView(BaseDuplicateCheckAPIView):
    serializer_class = SignupEmailCheckSerializer
    field_name = "email"
    error_message = "이미 사용중인 이메일입니다."
    success_message = "사용가능한 이메일입니다."

    @extend_schema(
        tags=["accounts"],
        summary="이메일 중복 확인 API",
        description="""
회원가입 시 사용할 이메일의 중복 여부를 확인합니다.

## 응답
- **200**: 사용 가능한 이메일
- **409**: 이미 사용 중인 이메일
        """,
        request=SignupEmailCheckSerializer,
        responses={
            200: OpenApiResponse(description="사용 가능한 이메일"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            409: OpenApiResponse(description="중복된 이메일"),
        },
    )
    def post(self, request: Request) -> Response:
        return super().post(request)


# 휴대폰 번호 중복 확인 api
class SignupPhoneCheckAPIView(BaseDuplicateCheckAPIView):
    serializer_class = SignupPhoneCheckSerializer
    field_name = "phone_number"
    error_message = "이미 사용중인 휴대폰 번호입니다."
    success_message = "사용가능한 휴대폰 번호입니다."

    def get_check_value(self, validated_data: dict) -> str:
        return normalize_phone_number(validated_data["phone_number"])

    @extend_schema(
        tags=["accounts"],
        summary="휴대폰 번호 중복 확인 API",
        description="""
회원가입 시 사용할 휴대폰 번호의 중복 여부를 확인합니다.

## 응답
- **200**: 사용 가능한 휴대폰 번호
- **409**: 이미 사용 중인 휴대폰 번호
        """,
        request=SignupPhoneCheckSerializer,
        responses={
            200: OpenApiResponse(description="사용 가능한 휴대폰 번호"),
            400: OpenApiResponse(description="유효성 검사 실패"),
            409: OpenApiResponse(description="중복된 휴대폰 번호"),
        },
    )
    def post(self, request: Request) -> Response:
        return super().post(request)
