from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.me import ChangePhoneRequestSerializer
from apps.users.services.me_service import (
    InvalidPhoneTokenError,
    PhoneNumberAlreadyExistsError,
    change_phone_number,
)


class ChangePhoneView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="휴대폰 번호 변경",
        description="""
휴대폰 번호를 변경합니다. SMS 인증 완료 후 발급받은 토큰이 필요합니다. 이미 등록된 휴대폰 번호로는 변경할 수 없습니다.

## 플로우

1. `POST /api/v1/accounts/verification/send-sms` - 새 휴대폰 번호로 인증 코드 발송
2. `POST /api/v1/accounts/verification/verify-sms` - 인증 코드 확인 → `sms_token` 반환
3. `PATCH /api/v1/accounts/change-phone` - `phone_verify_token`으로 휴대폰 번호 변경 (현재 API)

        """,
        request=ChangePhoneRequestSerializer,
        responses={
            200: OpenApiResponse(description="휴대폰 번호 변경에 성공하였습니다."),
            400: OpenApiResponse(description="유효하지 않거나 만료된 인증 토큰입니다."),
            409: OpenApiResponse(description="이미 등록된 휴대폰 번호입니다."),
        },
    )
    def patch(self, request: Request) -> Response:
        serializer = ChangePhoneRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_verify_token = serializer.validated_data["phone_verify_token"]

        try:
            updated_user = change_phone_number(user=request.user, phone_verify_token=phone_verify_token)  # type: ignore[arg-type]
        except InvalidPhoneTokenError as e:
            return Response(
                {"error_detail": {"phone_verify_token": [str(e)]}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PhoneNumberAlreadyExistsError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "detail": "휴대폰 번호 변경에 성공하였습니다.",
                "phone_number": updated_user.phone_number,
            },
            status=status.HTTP_200_OK,
        )
