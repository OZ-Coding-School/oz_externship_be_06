from typing import NoReturn

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.constants import ErrorMessages
from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin.questions_delete import (
    AdminExamQuestionDeleteResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.questions_delete import (
    ExamQuestionDeleteConflictError,
    ExamQuestionDeleteNotFoundError,
    delete_exam_question,
)
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamQuestionDeleteAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 문제 삭제 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamQuestionDeleteResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        raise PermissionDenied(detail=ErrorMessages.NO_QUESTION_DELETE_PERMISSION.value)

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 쪽지시험 문제 삭제 API",
        description="""
        스태프/관리자가 쪽지시험 문제를 삭제합니다.
        """,
        parameters=[
            OpenApiParameter(
                name="question_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="문제 ID",
            ),
        ],
        responses={
            200: AdminExamQuestionDeleteResponseSerializer,
            400: OpenApiResponse(
                ErrorResponseSerializer, description=ErrorMessages.INVALID_QUESTION_DELETE_REQUEST.value
            ),
            401: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.UNAUTHORIZED.value),
            403: OpenApiResponse(
                ErrorResponseSerializer, description=ErrorMessages.NO_QUESTION_DELETE_PERMISSION.value
            ),
            404: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.QUESTION_NOT_FOUND.value),
            409: OpenApiResponse(ErrorResponseSerializer, description=ErrorMessages.QUESTION_DELETE_CONFLICT.value),
        },
    )
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
