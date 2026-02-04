from __future__ import annotations

from dataclasses import dataclass

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
from rest_framework import status

from apps.courses.models import CohortStudent
from apps.exams.constants import ErrorMessages
from apps.exams.exceptions import ErrorDetailException
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.models.exam_submissions import ExamSubmission
from apps.exams.serializers.student.deployments_list import ExamListQuerySerializer


@dataclass(frozen=True)
class ExamListParams:
    user_id: int
    status: str


class ExamDeploymentListService:
    @staticmethod
    def _get_cohort_id(user_id: int) -> int:
        cohort_id = (
            CohortStudent.objects.filter(user_id=user_id)
            .order_by("created_at")
            .values_list("cohort_id", flat=True)
            .first()
        )
        if cohort_id is None:
            raise ErrorDetailException(ErrorMessages.USER_NOT_FOUND.value, status.HTTP_404_NOT_FOUND)
        return int(cohort_id)

    @staticmethod
    def _parse_status(params: dict[str, str]) -> str:
        query_serializer = ExamListQuerySerializer(data=params)
        if not query_serializer.is_valid():
            raise ErrorDetailException(ErrorMessages.INVALID_EXAM_LIST_REQUEST.value, status.HTTP_404_NOT_FOUND)
        return str(query_serializer.validated_data["status"])

    @classmethod
    def build_queryset(cls, params: ExamListParams) -> QuerySet[ExamDeployment]:
        latest_sub = ExamSubmission.objects.filter(
            submitter_id=params.user_id,
            deployment_id=OuterRef("pk"),
        ).order_by("-created_at")

        submission_id_sq = Subquery(latest_sub.values("id")[:1])
        score_sq = Subquery(latest_sub.values("score")[:1])
        correct_sq = Subquery(latest_sub.values("correct_answer_count")[:1])
        answers_json_sq = Subquery(latest_sub.values("answers_json")[:1])
        empty_json = Value({}, output_field=models.JSONField())

        qs = (
            ExamDeployment.objects.filter(cohort_id=cls._get_cohort_id(params.user_id))
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

        if params.status == "done":
            qs = qs.filter(exam_status="done")
        elif params.status == "pending":
            qs = qs.filter(exam_status="pending")

        return qs

    @classmethod
    def from_request(cls, *, user_id: int, query_params: dict[str, str]) -> QuerySet[ExamDeployment]:
        status_value = cls._parse_status(query_params)
        return cls.build_queryset(ExamListParams(user_id=user_id, status=status_value))
