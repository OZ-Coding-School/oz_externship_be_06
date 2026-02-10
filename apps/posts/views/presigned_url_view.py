from enum import Enum

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers.presigned_url import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.core.views.presigned_url import BasePresignedUrlAPIView

#게시글 이미지 업로드 도메인 및 S3 경로 정의
class StorageTarget(Enum):

    POST = ("post", "uploads/images/posts")

    def __init__(self, domain: str, s3_path: str):
        self.domain = domain
        self.s3_path = s3_path

#게시글 이미지 업로드용 Presigned URL 발급 API
class PostPresignedUrlAPIView(BasePresignedUrlAPIView):

    permission_classes = [IsAuthenticated]
    storage_target = StorageTarget.POST

    @extend_schema(
        summary="게시글 이미지 업로드 URL 발급",
        description="""
        S3의 'posts/' 경로로 이미지를 업로드하기 위한 presigned-URL을 발급합니다.

        """,
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=PresignedUrlResponseSerializer,
            ),
            400: OpenApiResponse(
                description="Bad Request",
            ),
            401: OpenApiResponse(
                description="Unauthorized",
            ),
        },
        tags=["posts"],
    )
    def put(self, request: Request) -> Response:
        return super().put(request)
