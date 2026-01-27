from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.find_email_serializer import FindEmailSerializer
from apps.users.utils.redis_utils import delete_sms_token, get_phone_by_token


# 이메일 마스킹 처리
def mask_email(email: str) -> str:
    try:
        local, domain = email.split("@")
        # 다중 TLD 처리 (예: .co.kr, .com.au)
        parts = domain.split(".")
        if len(parts) >= 3 and len(parts[-1]) == 2:
            # 국가 코드 TLD인 경우 (예: example.co.kr)
            domain_name = ".".join(parts[:-2])
            domain_ext = ".".join(parts[-2:])
        else:
            domain_name = ".".join(parts[:-1])
            domain_ext = parts[-1]
    except (ValueError, IndexError):
        return email

    # 로컬 파트 마스킹 (2자 이하는 그대로 유지)
    if len(local) <= 2:
        masked_local = local
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

    # 도메인 파트 마스킹 (2자 이하는 그대로 유지)
    if len(domain_name) <= 2:
        masked_domain = domain_name
    else:
        masked_domain = domain_name[0] + "*" * (len(domain_name) - 2) + domain_name[-1]

    return f"{masked_local}@{masked_domain}.{domain_ext}"


# 이메일 찾기
class FindEmailAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="이메일 찾기 API",
        description="""
가입된 이메일을 찾습니다. SMS 인증이 완료된 상태에서 사용합니다.

## 플로우

1. `POST /api/v1/accounts/verification/send-sms` - 가입 시 등록한 휴대폰 번호로 인증 코드 발송
2. `POST /api/v1/accounts/verification/verify-sms` - 인증 코드 확인 → `sms_token` 반환
3. `POST /api/v1/accounts/find-email` - 이메일 찾기 (현재 API)

## 응답
- `email`: 마스킹 처리된 이메일 (예: `u**r@e*****e.com`)

## 마스킹 규칙
- 이메일 로컬 파트: 첫 글자와 마지막 글자만 표시, 중간은 `*`로 대체
- 도메인 파트: 첫 글자와 마지막 글자만 표시, 중간은 `*`로 대체
        """,
        request=FindEmailSerializer,
        responses={
            200: OpenApiResponse(description="이메일 찾기 성공"),
            400: OpenApiResponse(description="유효성 검사 실패 또는 인증 실패"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = FindEmailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        name = serializer.validated_data["name"]
        sms_token = serializer.validated_data["sms_token"]
        phone_number = get_phone_by_token(sms_token)

        if not phone_number:
            return Response(
                {"error_detail": {"sms_token": ["유효하지 않거나 만료된 SMS 인증 토큰입니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(name=name, phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"error_detail": {"name": ["일치하는 사용자 정보를 찾을 수 없습니다."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        delete_sms_token(sms_token)

        masked = mask_email(user.email)

        return Response(
            {"email": masked},
            status=status.HTTP_200_OK,
        )
