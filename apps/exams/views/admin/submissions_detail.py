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
from apps.exams.error_map import raise_error
from apps.exams.serializers.admin.submissions_delete import (
    AdminExamSubmissionDeleteResponseSerializer,
)
from apps.exams.serializers.admin.submissions_detail import (
    AdminExamSubmissionDetailResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.submissions_delete import delete_exam_submission
from apps.exams.services.admin.submissions_detail import get_admin_submission_detail
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


class AdminExamSubmissionDetailAPIView(ExamsExceptionMixin, APIView):
    """어드민 쪽지시험 응시 내역 상세 조회/삭제 API."""

    permission_classes = [IsAuthenticated, IsStaffRole]
    serializer_class = AdminExamSubmissionDetailResponseSerializer

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated()
        detail_message = (
            ErrorMessages.NO_SUBMISSION_DELETE_PERMISSION.value
            if request.method == "DELETE"
            else ErrorMessages.NO_SUBMISSION_DETAIL_PERMISSION.value
        )
        raise PermissionDenied(detail=detail_message)

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 응시 내역 상세 조회",
        description="쪽지시험 응시 내역 상세 정보를 조회합니다.",
        responses={
            200: AdminExamSubmissionDetailResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 상세 조회 요청",
                        value={"error_detail": ErrorMessages.INVALID_SUBMISSION_DETAIL_REQUEST.value},
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
                        value={"error_detail": ErrorMessages.NO_SUBMISSION_DETAIL_PERMISSION.value},
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "응시 내역 없음",
                        value={"error_detail": ErrorMessages.SUBMISSION_DETAIL_NOT_FOUND.value},
                    ),
                ],
            ),
        },
    )
    def get(self, request: Request, submission_id: int) -> Response:
        parse_positive_int(submission_id, ErrorMessages.INVALID_SUBMISSION_DETAIL_REQUEST)

        payload = get_admin_submission_detail(submission_id)
        serializer = self.serializer_class(instance=payload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 응시 내역 삭제",
        description="쪽지시험 응시 내역을 삭제합니다.",
        responses={
            200: AdminExamSubmissionDeleteResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 응시 내역 삭제 요청",
                        value={"error_detail": ErrorMessages.INVALID_SUBMISSION_DELETE_REQUEST.value},
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
                        value={"error_detail": ErrorMessages.NO_SUBMISSION_DELETE_PERMISSION.value},
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "응시 내역 없음",
                        value={"error_detail": ErrorMessages.SUBMISSION_DELETE_NOT_FOUND.value},
                    ),
                ],
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "응시 내역 삭제 충돌",
                        value={"error_detail": ErrorMessages.SUBMISSION_DELETE_CONFLICT.value},
                    ),
                ],
            ),
        },
    )
    def delete(self, request: Request, submission_id: int) -> Response:
        parse_positive_int(submission_id, ErrorMessages.INVALID_SUBMISSION_DELETE_REQUEST)

        result = delete_exam_submission(submission_id)
        serializer = AdminExamSubmissionDeleteResponseSerializer(data=result)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
