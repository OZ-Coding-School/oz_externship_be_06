from typing import NoReturn

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.questions_delete import (
    AdminExamQuestionDeleteResponseSerializer,
)
from apps.exams.services.admin.questions_delete import (
    ExamQuestionDeleteConflictError,
    ExamQuestionDeleteNotFoundError,
    delete_exam_question,
)
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamQuestionDeleteAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 문제 삭제 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamQuestionDeleteResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_QUESTION_DELETE_PERMISSION.value)

    def delete(self, request: Request, question_id: int) -> Response:
        if question_id <= 0:
            return Response(
                {"error_detail": ErrorMessages.INVALID_QUESTION_DELETE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = delete_exam_question(question_id)
        except ExamQuestionDeleteNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.QUESTION_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamQuestionDeleteConflictError:
            return Response(
                {"error_detail": ErrorMessages.QUESTION_DELETE_CONFLICT.value},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.serializer_class(data=result)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
