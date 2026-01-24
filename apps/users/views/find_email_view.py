from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.find_email_serializer import FindEmailSerializer
from apps.users.utils.redis_utils import delete_sms_token, get_phone_by_token

#이메일 마스킹 처리
def mask_email(email: str) -> str:
    try:
        local, domain = email.split("@")
        domain_name, domain_ext = domain.rsplit(".", 1)
    except ValueError:
        return email

    # 로컬 파트 마스킹
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

    # 도메인 파트 마스킹
    if len(domain_name) <= 2:
        masked_domain = domain_name[0] + "*"
    else:
        masked_domain = domain_name[0] + "*" * (len(domain_name) - 2) + domain_name[-1]

    return f"{masked_local}@{masked_domain}.{domain_ext}"

#이메일 찾기
class FindEmailAPIView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["accounts"],
        summary="이메일 찾기 API",
        description="""
        이름과 SMS 인증 토큰을 사용하여 가입된 이메일을 찾습니다.
        이메일은 마스킹 처리되어 반환됩니다. (예: u**r@e****le.com)
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
