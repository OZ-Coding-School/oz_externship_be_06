from enum import Enum
from typing import Any, NoReturn

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers.presigned_url import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.core.utils.permissions import IsStaffRole
from apps.core.views.presigned_url import BasePresignedUrlAPIView


class StorageTarget(Enum):

    COURSE_THUMBNAIL = ("course_thumbnail", "uploads/images/courses/thumbnails")

    def __init__(self, domain: str, s3_path: str):
        self.domain = domain
        self.s3_path = s3_path


class CoursePresignedUrlAPIView(BasePresignedUrlAPIView):

    storage_target = StorageTarget.COURSE_THUMBNAIL
    serializer_class = PresignedUrlRequestSerializer

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    @extend_schema(
        summary="과정 썸네일 업로드 URL 발급",
        description="S3의 courses 경로로 과정 썸네일을 업로드하기 위한 presigned URL을 발급합니다.",
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=PresignedUrlResponseSerializer,
            ),
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
        },
        tags=["admin_courses"],
    )
    def put(self, request: Request) -> Response:
        return super().put(request)

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail="권한이 없습니다.")
