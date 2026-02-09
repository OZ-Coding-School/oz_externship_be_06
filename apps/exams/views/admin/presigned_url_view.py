from enum import Enum
from typing import Any, NoReturn

from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStaffRole
from apps.core.views.presigned_url import BasePresignedUrlAPIView
from apps.exams.constants import ErrorMessages
from apps.exams.schemas.admin import admin_exam_presigned_url_schema
from apps.exams.views.mixins import ExamsExceptionMixin


class StorageTarget(Enum):
    """
    시험 썸네일 업로드용 S3 경로 정의
    """

    EXAM_THUMBNAIL = ("exam_thumbnail", "uploads/images/exams")

    def __init__(self, domain: str, s3_path: str):
        self.domain = domain
        self.s3_path = s3_path


# 시험 썸네일 업로드 URL 발급
class ExamPresignedUrlAPIView(ExamsExceptionMixin, BasePresignedUrlAPIView):
    """
    어드민 시험 썸네일 업로드용 Presigned URL 발급 API
    """

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStaffRole()]

    parser_classes = [JSONParser]

    storage_target = StorageTarget.EXAM_THUMBNAIL

    @admin_exam_presigned_url_schema
    def put(self, request: Request) -> Response:
        return super().put(request)

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.FORBIDDEN.value)
