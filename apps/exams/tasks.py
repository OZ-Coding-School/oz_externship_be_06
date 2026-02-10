from __future__ import annotations

from datetime import timedelta

from celery import shared_task  # type: ignore[import-untyped]
from django.db.models import DateTimeField, DurationField, ExpressionWrapper, F, Q
from django.utils import timezone

from apps.exams.models import ExamSubmission
from apps.exams.services.student.auto_submit import auto_submit_if_overdue


@shared_task  # type: ignore[misc]
def auto_submit_overdue_exams() -> int:
    """마감된 시험 제출을 강제 제출로 처리합니다."""
    now = timezone.now()
    duration_expr = ExpressionWrapper(
        F("deployment__duration_time") * timedelta(minutes=1),
        output_field=DurationField(),
    )
    deadline_expr = ExpressionWrapper(
        F("started_at") + duration_expr,
        output_field=DateTimeField(),
    )
    queryset = (
        ExamSubmission.objects.select_related("deployment")
        .annotate(deadline=deadline_expr)
        .filter(Q(answers_json={}) | Q(answers_json=[]), deadline__lt=now)
        .only("id", "deployment_id", "submitter_id", "started_at")
    )
    processed = 0
    for submission in queryset.iterator():
        result = auto_submit_if_overdue(
            deployment=submission.deployment,
            user_id=submission.submitter_id,
            now=now,
        )
        if result.submitted:
            processed += 1
    return processed
