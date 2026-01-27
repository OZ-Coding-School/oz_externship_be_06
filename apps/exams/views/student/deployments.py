from __future__ import annotations

from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    CharField,
    Count,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.utils.pagination import SimplePagePagination
from apps.courses.models import CohortStudent
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.models.exam_submissions import ExamSubmission
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.deployments import ExamDeploymentListSerializer


@extend_schema(
    tags=["exams"],
    summary="시험 배포 목록 조회",
    description="현재 로그인한 사용자의 코호트 기준으로 시험 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="status",
            description="시험 상태 필터",
            required=False,
            type=str,
            enum=["all", "done", "pending"],
            default="all",
        ),
    ],
    responses={
        200: ExamDeploymentListSerializer,
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": "권한이 없습니다."},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "코호트 없음/잘못된 요청",
                    value={"error_detail": "사용자 정보를 찾을 수 없습니다."},
                ),
                OpenApiExample(
                    "잘못된 status",
                    value={"error_detail": "요청 코드가 일치하지 않습니다."},
                ),
            ],
        ),
    },
)
class ExamListView(ListAPIView[ExamDeployment]):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamDeploymentListSerializer
    pagination_class = SimplePagePagination

    def handle_exception(self, exc: Exception) -> Response:
        if isinstance(exc, NotAuthenticated):
            exc = ErrorDetailException("자격 인증 데이터가 제공되지 않았습니다.", status.HTTP_401_UNAUTHORIZED)

        elif isinstance(exc, PermissionDenied):
            exc = ErrorDetailException("권한이 없습니다.", status.HTTP_403_FORBIDDEN)

        if isinstance(exc, ErrorDetailException):
            return Response({"error_detail": str(exc.detail)}, status=exc.http_status)

        return super().handle_exception(exc)

    def get_queryset(self) -> QuerySet[ExamDeployment]:
        user_id = self.request.user.id
        assert user_id is not None
        cohort_id = (
            CohortStudent.objects.filter(user_id=user_id)
            .order_by("created_at")
            .values_list("cohort_id", flat=True)
            .first()
        )

        if cohort_id is None:
            raise ErrorDetailException("사용자 정보를 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)

        status_param = self.request.query_params.get("status", "all").lower()
        if status_param not in ("all", "done", "pending"):
            raise ErrorDetailException("요청 코드가 일치하지 않습니다.", status.HTTP_404_NOT_FOUND)

        latest_sub = ExamSubmission.objects.filter(submitter_id=user_id, deployment_id=OuterRef("pk")).order_by(
            "-created_at"
        )

        submission_id_sq = Subquery(latest_sub.values("id")[:1])
        score_sq = Subquery(latest_sub.values("score")[:1])
        correct_sq = Subquery(latest_sub.values("correct_answer_count")[:1])
        answers_json_sq = Subquery(latest_sub.values("answers_json")[:1])
        empty_json = Value({}, output_field=models.JSONField())

        qs = (
            ExamDeployment.objects.filter(cohort_id=cohort_id)
            .select_related("exam__subject")
            .annotate(
                question_count=Count("exam__questions", distinct=True),
                total_score=Coalesce(
                    Sum("exam__questions__point", distinct=True),
                    Value(0),
                    output_field=IntegerField(),
                ),
                submission_id=submission_id_sq,
                score=Coalesce(score_sq, Value(0), output_field=IntegerField()),
                correct_answer_count=Coalesce(correct_sq, Value(0), output_field=IntegerField()),
                answers_json=answers_json_sq,
            )
            .annotate(
                exam_status=Case(
                    When(submission_id__isnull=True, then=Value("pending")),
                    When(answers_json=empty_json, then=Value("pending")),
                    default=Value("done"),
                    output_field=CharField(),
                ),
                is_done=Case(
                    When(submission_id__isnull=True, then=Value(False)),
                    When(answers_json=empty_json, then=Value(False)),
                    default=Value(True),
                    output_field=BooleanField(),
                ),
            )
            .order_by("-created_at")
        )

        if status_param == "done":
            qs = qs.filter(exam_status="done")
        elif status_param == "pending":
            qs = qs.filter(exam_status="pending")

        return qs
