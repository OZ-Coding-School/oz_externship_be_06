from typing import NoReturn

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.exams_delete import (
    AdminExamDeleteResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.exams_delete import (
    ExamDeleteConflictError,
    ExamDeleteNotFoundError,
    delete_exam,
)
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["admin_exams"],
    summary="어드민 시험 삭제",
    description="쪽지시험을 삭제합니다.",
    responses={
        200: AdminExamDeleteResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 요청",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_DELETE_REQUEST.value},
                ),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                ),
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_EXAM_DELETE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_DELETE_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "삭제 충돌",
                    value={"error_detail": ErrorMessages.EXAM_DELETE_CONFLICT.value},
                ),
            ],
        ),
    },
)
class AdminExamDeleteAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 삭제 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamDeleteResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=ErrorMessages.NO_EXAM_DELETE_PERMISSION.value)

    def delete(self, request: Request, exam_id: int) -> Response:
        if exam_id <= 0:
            return Response(
                {"error_detail": ErrorMessages.INVALID_EXAM_DELETE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            deleted_id = delete_exam(exam_id)
        except ExamDeleteNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.EXAM_DELETE_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamDeleteConflictError:
            return Response(
                {"error_detail": ErrorMessages.EXAM_DELETE_CONFLICT.value},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.serializer_class({"id": deleted_id})
        return Response(serializer.data, status=status.HTTP_200_OK)
