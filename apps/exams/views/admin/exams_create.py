from __future__ import annotations

from typing import NoReturn

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.serializers.admin.exams_create import (
    AdminExamCreateRequestSerializer,
    AdminExamCreateResponseSerializer,
)
from apps.exams.services.admin.exams_create import create_exam
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamCreateAPIView(ExamsExceptionMixin, APIView):
    """관리자 쪽지시험 생성 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = AdminExamCreateRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_EXAM_CREATE_PERMISSION.value)

    def post(self, request: Request) -> Response:
        serializer = AdminExamCreateRequestSerializer(data=request.data)

        if not serializer.is_valid():
            raise_error(ErrorMessages.INVALID_EXAM_CREATE_REQUEST)

        data = serializer.validated_data
        exam = create_exam(
            title=data["title"],
            subject_id=data["subject_id"],
            thumbnail_img=data.get("thumbnail_img"),
        )

        response_serializer = AdminExamCreateResponseSerializer(exam)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
