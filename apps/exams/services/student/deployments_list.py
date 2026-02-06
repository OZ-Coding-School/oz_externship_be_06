from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias, TypedDict, cast

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
from django.db.models.fields.json import KeyTextTransform, KeyTransform
from django.db.models.functions import Cast, Coalesce, JSONObject
from apps.courses.models import CohortStudent
from apps.exams.constants import ErrorMessages
from apps.exams.error_map import raise_error
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.models.exam_submissions import ExamSubmission
from apps.exams.serializers.student.deployments_list import ExamListQuerySerializer


@dataclass(frozen=True)
class ExamListParams:
    user_id: int
    cohort_id: int
    status: str


class ExamDeploymentAnnotations(TypedDict):
    exam_status: str
    is_done: bool


if TYPE_CHECKING:
    from django_stubs_ext import WithAnnotations

    ExamDeploymentAnnotated: TypeAlias = WithAnnotations[ExamDeployment, ExamDeploymentAnnotations]
    ExamDeploymentAnnotatedQS: TypeAlias = QuerySet[ExamDeploymentAnnotated]
else:
    ExamDeploymentAnnotatedQS: TypeAlias = QuerySet[ExamDeployment]


class ExamDeploymentListService:
    # 최신 제출 1건을 JSON으로 패킹해 단일 서브쿼리로 조회.
    @staticmethod
    def _build_latest_submission_json(user_id: int) -> Subquery:
        latest_sub = ExamSubmission.objects.filter(
            submitter_id=user_id,
            deployment_id=OuterRef("pk"),
        ).order_by("-created_at")

        return Subquery(
            latest_sub.annotate(
                payload=JSONObject(
                    id="id",
                    score="score",
                    correct_answer_count="correct_answer_count",
                    answers_json="answers_json",
                )
            ).values("payload")[:1],
            output_field=models.JSONField(),
        )

    # JSON 패킹 결과에서 필요한 필드를 꺼내 annotate 용도로 구성.
    @staticmethod
    def _build_submission_annotations(submission_json_sq: Subquery) -> dict[str, models.Expression]:
        return {
            "submission_id": Cast(KeyTextTransform("id", submission_json_sq), IntegerField()),
            "score": Coalesce(
                Cast(KeyTextTransform("score", submission_json_sq), IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
            "correct_answer_count": Coalesce(
                Cast(KeyTextTransform("correct_answer_count", submission_json_sq), IntegerField()),
                Value(0),
                output_field=IntegerField(),
            ),
            "answers_json": KeyTransform("answers_json", submission_json_sq),
        }

    # 응시 상태/완료 여부 계산 로직을 별도 annotate로 분리.
    @staticmethod
    def _build_status_annotations() -> dict[str, models.Expression]:
        empty_json = Value({}, output_field=models.JSONField())
        return {
            "exam_status": Case(
                When(submission_id__isnull=True, then=Value("pending")),
                When(answers_json=empty_json, then=Value("pending")),
                default=Value("done"),
                output_field=CharField(),
            ),
            "is_done": Case(
                When(submission_id__isnull=True, then=Value(False)),
                When(answers_json=empty_json, then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            ),
        }

    # 코호트 조회 + status 파라미터 검증을 한 번에 수행.
    @staticmethod
    def _validate_request(user_id: int, params: dict[str, str]) -> ExamListParams:
        cohort_id = (
            CohortStudent.objects.filter(user_id=user_id)
            .order_by("created_at")
            .values_list("cohort_id", flat=True)
            .first()
        )
        if cohort_id is None:
            raise_error(ErrorMessages.USER_NOT_FOUND)

        query_serializer = ExamListQuerySerializer(data=params)
        if not query_serializer.is_valid():
            raise_error(ErrorMessages.INVALID_EXAM_LIST_REQUEST, status_override=404)

        return ExamListParams(
            user_id=user_id,
            cohort_id=int(cohort_id),
            status=str(query_serializer.validated_data["status"]),
        )

    # 검증된 파라미터로 학생 시험 목록 조회용 QuerySet 구성.
    @classmethod
    def build_queryset(cls, params: ExamListParams) -> QuerySet[ExamDeployment]:
        submission_json_sq = cls._build_latest_submission_json(params.user_id)
        qs = (
            ExamDeployment.objects.filter(cohort_id=params.cohort_id)
            .select_related("exam__subject")
            .annotate(
                question_count=Count("exam__questions", distinct=True),
                total_score=Coalesce(
                    Sum("exam__questions__point", distinct=True),
                    Value(0),
                    output_field=IntegerField(),
                ),
                **cls._build_submission_annotations(submission_json_sq),
            )
            .annotate(
                **cls._build_status_annotations(),
            )
            .order_by("-created_at")
        )

        status_filter = {"done": "done", "pending": "pending"}
        annotated_qs = cast(ExamDeploymentAnnotatedQS, qs)

        if params.status in status_filter:
            annotated_qs = annotated_qs.filter(exam_status=status_filter[params.status])

        return cast(QuerySet[ExamDeployment], annotated_qs)

    # 요청 파라미터를 검증하고 목록 조회 쿼리를 구성.
    @classmethod
    def from_request(cls, *, user_id: int, query_params: dict[str, str]) -> QuerySet[ExamDeployment]:
        params = cls._validate_request(user_id, query_params)
        return cls.build_queryset(params)
