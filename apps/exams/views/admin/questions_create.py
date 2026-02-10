from typing import NoReturn

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.schemas.admin import admin_exam_question_create_schema
from apps.exams.serializers.admin.questions_create import (
    AdminExamQuestionCreateRequestSerializer,
    AdminExamQuestionCreateResponseSerializer,
)
from apps.exams.services.admin.questions_create import create_exam_question
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


@admin_exam_question_create_schema
class AdminExamQuestionCreateAPIView(ExamsExceptionMixin, APIView):
    # 어드민 문제 등록
    """어드민 쪽지시험 문제 등록 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamQuestionCreateRequestSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_QUESTION_CREATE_PERMISSION.value)

    def post(self, request: Request, exam_id: int) -> Response:
        parse_positive_int(exam_id, ErrorMessages.INVALID_QUESTION_CREATE_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            raise_error(ErrorMessages.INVALID_QUESTION_CREATE_REQUEST)

        result = create_exam_question(exam_id, serializer.validated_data)

        return Response(AdminExamQuestionCreateResponseSerializer(result).data, status=status.HTTP_201_CREATED)
