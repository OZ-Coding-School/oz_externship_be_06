from enum import Enum

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers.presigned_url import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.core.views.presigned_url import BasePresignedUrlAPIView
from apps.users.serializers.me import ProfileImageUrlRequestSerializer
from apps.users.services.me_service import save_profile_image_url


class StorageTarget(Enum):

    PROFILE = ("profile", "uploads/images/profiles")

    def __init__(self, domain: str, s3_path: str):
        self.domain = domain
        self.s3_path = s3_path


# 프로필 이미지 업로드용 Presigned URL 발급 API
class ProfilePresignedUrlAPIView(BasePresignedUrlAPIView):

    permission_classes = [IsAuthenticated]
    storage_target = StorageTarget.PROFILE

    @extend_schema(
        tags=["accounts"],
        summary="프로필 이미지 업로드 URL 발급",
        description="""
프로필 이미지를 S3에 업로드하기 위한 presigned-URL을 발급합니다.
        """,
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=PresignedUrlResponseSerializer,
            ),
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="Unauthorized"),
        },
    )
    def put(self, request: Request) -> Response:
        return super().put(request)


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="프로필 이미지 수정",
        description="""
프로필 이미지 URL을 저장합니다.

## 주의사항
- presigned URL로 S3에 이미지를 업로드한 후 호출해야 합니다.
- 기존 프로필 이미지가 있는 경우 S3에서 자동으로 삭제됩니다.
        """,
        request=ProfileImageUrlRequestSerializer,
        responses={
            200: OpenApiResponse(description="프로필 사진이 등록되었습니다."),
            400: OpenApiResponse(description="잘못된 요청입니다."),
        },
    )
    def patch(self, request: Request) -> Response:
        serializer = ProfileImageUrlRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile_img_url = serializer.validated_data["profile_img_url"]

        save_profile_image_url(user=request.user, profile_img_url=profile_img_url)  # type: ignore[arg-type]

        return Response(
            {"detail": "프로필 사진이 등록되었습니다."},
            status=status.HTTP_200_OK,
        )
