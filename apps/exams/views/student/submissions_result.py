from typing import cast

from django.http import Http404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.exams.exceptions import ErrorDetailException
from apps.exams.models import ExamSubmission
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.submissions_result import ExamSubmissionSerializer
from apps.exams.services.student.submissions_result import get_exam_submission_detail


@extend_schema(
    tags=["exams"],
    summary="시험 제출 결과 상세 조회",
    description="submission_id로 시험 제출(결과) 상세 정보를 조회합니다.",
    responses={
        200: ExamSubmissionSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 시험 응시 세션",
                    value={"error_detail": "유효하지 않은 시험 응시 세션입니다."},
                ),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                ),
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": "권한이 없습니다."},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": "해당 시험 정보를 찾을 수 없습니다."},
                ),
            ],
        ),
    },
)
class ExamSubmissionDetailView(RetrieveAPIView[ExamSubmission]):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamSubmissionSerializer

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            exc = ErrorDetailException("자격 인증 데이터가 제공되지 않았습니다.", status.HTTP_401_UNAUTHORIZED)
        elif isinstance(exc, PermissionDenied):
            exc = ErrorDetailException("권한이 없습니다.", status.HTTP_403_FORBIDDEN)

        if isinstance(exc, Http404):
            exc = ErrorDetailException("제출 내역을 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)

        if isinstance(exc, ErrorDetailException):
            return Response({"error_detail": str(exc.detail)}, status=exc.http_status)

        return super().handle_exception(exc)

    def get_object(self) -> ExamSubmission:
        submission_id = int(self.kwargs["submission_id"])
        user_id = cast(int, self.request.user.id)

        return get_exam_submission_detail(
            submission_id=submission_id,
            user_id=user_id,
        )
