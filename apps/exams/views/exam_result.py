from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from apps.exams.serializers.error import ErrorDetailSerializer
from apps.exams.serializers.exam_result import ExamSubmissionSerializer
from apps.exams.models import ExamSubmission
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from apps.exams.exceptions import ErrorDetailException

@extend_schema(
    tags=["exams"],
    summary="시험 제출 결과 상세 조회",
    description="submission_id로 시험 제출(결과) 상세 정보를 조회합니다.",
    responses={
        200: ExamSubmissionSerializer,

        400: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 시험 응시 세션",
                    value={"error_detail": "유효하지 않은 시험 응시 세션입니다."},
                ),
            ],
        ),
        401: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                ),
            ],
        ),
        403: OpenApiResponse(
            response=ErrorDetailSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": "권한이 없습니다."},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorDetailSerializer,
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
class ExamSubmissionDetailView(RetrieveAPIView):
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

    def get_object(self):
        submission_id = self.kwargs["submission_id"]
        user_id = self.request.user.id

        submission = get_object_or_404(
            ExamSubmission.objects.select_related("deployment", "deployment__exam"),
            id=submission_id,
        )

        if submission.submitter_id != user_id:
            raise PermissionDenied()

        if submission.answers_json == {}:
            raise ErrorDetailException(
                "유효하지 않은 시험 응시 세션입니다.",
                status.HTTP_400_BAD_REQUEST,
            )

        return submission