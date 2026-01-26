from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.me import ProfileImageRequestSerializer
from apps.users.services.me_service import update_profile_image


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=["accounts"],
        summary="프로필 이미지 수정",
        request=ProfileImageRequestSerializer,
        responses={
            200: OpenApiResponse(description="프로필 사진이 등록되었습니다."),
            400: OpenApiResponse(description="잘못된 파일 형식입니다."),
        },
    )
    def patch(self, request: Request) -> Response:
        serializer = ProfileImageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data["image"]

        # 파일 형식 검증
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if image.content_type not in allowed_types:
            return Response(
                {"error_detail": "잘못된 파일 형식입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        update_profile_image(user=request.user, image=image)  # type: ignore[arg-type]

        return Response(
            {"detail": "프로필 사진이 등록되었습니다."},
            status=status.HTTP_200_OK,
        )
