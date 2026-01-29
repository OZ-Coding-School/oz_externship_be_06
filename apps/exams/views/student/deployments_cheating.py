from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStudentRole
from apps.exams.constants import ErrorMessages, ExamStatus
from apps.exams.models import ExamDeployment, ExamSubmission
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.deployments_cheating import (
    ExamCheatingRequestSerializer,
    ExamCheatingResponseSerializer,
)
from apps.exams.services.answers_json import normalize_answers_json
from apps.exams.services.grading import grade_submission
from apps.exams.services.student.deployments_status import (
    get_exam_status,
    is_deployment_active_now,
)
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
        user = request.user

        try:
            deployment = ExamDeployment.objects.select_related("exam", "cohort").get(id=deployment_id)
        except ExamDeployment.DoesNotExist:
            return Response(
                {"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not is_deployment_active_now(deployment):
            return Response(
                {"error_detail": ErrorMessages.EXAM_ALREADY_CLOSED.value},
                status=status.HTTP_410_GONE,
            )

        cheating_key = f"exam:cheating:{deployment.id}:{user.id}"
        submit_lock_key = f"exam:submit-lock:{deployment.id}:{user.id}"
        if ExamSubmission.objects.filter(submitter_id=user.id, deployment=deployment).exists():
            return Response(
                {"error_detail": ErrorMessages.SUBMISSION_ALREADY_SUBMITTED.value},
                status=status.HTTP_409_CONFLICT,
            )

        current_count = cache.get(cheating_key)
        ttl_seconds = max(1, deployment.duration_time * 60)
        if current_count is None:
            cheating_count = 1
            cache.set(cheating_key, 1, timeout=ttl_seconds)
        elif current_count >= 3:
            cheating_count = int(current_count)
        else:
            cheating_count = cache.incr(cheating_key)

        is_closed = cheating_count >= 3
        if is_closed:
            request_serializer = ExamCheatingRequestSerializer(data=request.data)
            request_serializer.is_valid(raise_exception=True)
            answers_json = normalize_answers_json(request_serializer.validated_data.get("answers_json", []))

            if cache.add(submit_lock_key, "1", timeout=5):
                with transaction.atomic():
                    submission, created = ExamSubmission.objects.select_for_update().get_or_create(
                        submitter_id=user.id,
                        deployment=deployment,
                        defaults={
                            "started_at": timezone.now(),
                            "cheating_count": cheating_count,
                            "answers_json": answers_json,
                        },
                    )
                    if not created:
                        submission.cheating_count = cheating_count
                        submission.answers_json = answers_json
                        submission.save(update_fields=["cheating_count", "answers_json"])
                    grade_submission(submission)
                cache.delete(submit_lock_key)
        status_value = ExamStatus.CLOSED.value if is_closed else get_exam_status(deployment).value
        serializer = self.serializer_class(
            data={
                "cheating_count": cheating_count,
                "exam_status": status_value,
                "force_submit": is_closed,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
