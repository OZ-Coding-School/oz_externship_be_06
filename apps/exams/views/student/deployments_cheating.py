from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStudentRole
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.core.serializers.error import ErrorResponseSerializer
from apps.exams.serializers.student.deployments_cheating import (
    ExamCheatingRequestSerializer,
    ExamCheatingResponseSerializer,
)
from apps.exams.services.student.deployments_cheating import update_cheating_count
from apps.exams.services.student.deployments_status import get_deployment_or_404
from apps.exams.validators import parse_positive_int
from apps.exams.views.mixins import ExamsExceptionMixin


@extend_schema(
    tags=["exams"],
    summary="부정행위 횟수 갱신",
    description="부정행위 횟수를 증가시키고 강제 제출 여부를 판단합니다.",
    request=ExamCheatingRequestSerializer,
    responses={
        200: ExamCheatingResponseSerializer,
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
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "이미 제출됨",
                    value={"error_detail": ErrorMessages.SUBMISSION_ALREADY_SUBMITTED.value},
                ),
            ],
        ),
        410: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Gone",
            examples=[
                OpenApiExample(
                    "시험 종료",
                    value={"error_detail": ErrorMessages.EXAM_ALREADY_CLOSED.value},
                ),
            ],
        ),
    },
)
class ExamCheatingUpdateAPIView(ExamsExceptionMixin, APIView):
    """부정행위 횟수를 증가시키고 종료 여부를 판단."""

    permission_classes = [IsAuthenticated, IsStudentRole]
    serializer_class = ExamCheatingResponseSerializer

    def post(self, request: Request, deployment_id: int) -> Response:
        parse_positive_int(deployment_id, ErrorMessages.EXAM_NOT_FOUND)
        user = request.user

        deployment = get_deployment_or_404(deployment_id, error_message=ErrorMessages.EXAM_NOT_FOUND)

        request_serializer = ExamCheatingRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        user_id = user.id
        if user_id is None:
            raise_error(ErrorMessages.UNAUTHORIZED)

        result = update_cheating_count(
            deployment=deployment,
            user_id=user_id,
            answers_json=request_serializer.validated_data.get("answers_json", []),
        )

        serializer = self.serializer_class(
            data={
                "cheating_count": result.cheating_count,
                "exam_status": result.exam_status,
                "force_submit": result.force_submit,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
