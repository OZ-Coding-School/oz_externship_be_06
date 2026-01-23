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
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.core.utils.pagination import SimplePagePagination
from apps.courses.models.cohort_students import CohortStudent
from apps.exams.models.exam_deployments import ExamDeployment
from apps.exams.models.exam_submissions import ExamSubmission
from apps.exams.serializers.exam_list import ExamDeploymentListSerializer


class ExamListView(ListAPIView[ExamDeployment]):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamDeploymentListSerializer
    pagination_class = SimplePagePagination

    def get_queryset(self) -> QuerySet[ExamDeployment]:
        user_id = self.request.user.id
        # 🔥 여기 추가
        cohort_id = (
            CohortStudent.objects.filter(user_id=user_id)  # type: ignore[attr-defined]
            .order_by("created_at")
            .values_list("cohort_id", flat=True)
            .first()
        )

        if not cohort_id:
            raise ValidationError("해당 유저의 코호트 정보가 없습니다.")

        status_param = self.request.query_params.get("status", "all").lower()
        if status_param not in ("all", "done", "pending"):
            raise ValidationError({"status": "status는 all/done/pending 중 하나여야 합니다."})

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
