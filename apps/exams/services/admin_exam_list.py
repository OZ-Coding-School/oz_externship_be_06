from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.db.models import Count, Q, QuerySet

from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam


class InvalidAdminExamListParams(Exception):
    """어드민 시험 목록 조회 파라미터가 유효하지 않을 때"""


@dataclass(frozen=True)
class AdminExamListParams:
    search_keyword: Optional[str] = None
    subject_id: Optional[int] = None
    sort: str = "created_at"
    order: str = "desc"


class AdminExamListService:
    ALLOWED_SORT = {"created_at", "title"}
    ALLOWED_ORDER = {"asc", "desc"}
    DEFAULT_SORT = "created_at"
    DEFAULT_ORDER = "desc"

    @classmethod
    def parse_params(
        cls, *, search_keyword: str | None, subject_id: str | None, sort: str | None, order: str | None
    ) -> AdminExamListParams:
        sort_v = sort or cls.DEFAULT_SORT
        order_v = order or cls.DEFAULT_ORDER

        if sort_v not in cls.ALLOWED_SORT or order_v not in cls.ALLOWED_ORDER:
            raise InvalidAdminExamListParams(ErrorMessages.INVALID_SUBMISSION_LIST_REQUEST.value)

        subject_id_v: int | None = None
        if subject_id:
            try:
                subject_id_v = int(subject_id)
            except ValueError:
                raise InvalidAdminExamListParams(ErrorMessages.INVALID_EXAM_LIST_REQUEST.value)

        return AdminExamListParams(
            search_keyword=search_keyword or None,
            subject_id=subject_id_v,
            sort=sort_v,
            order=order_v,
        )

    @classmethod
    def get_queryset(cls, params: AdminExamListParams) -> QuerySet[Exam]:
        qs = Exam.objects.select_related("subject").annotate(
            question_count=Count("questions", distinct=True),
            submit_count=Count("deployments__submissions", distinct=True),
        )

        if params.search_keyword:
            qs = qs.filter(Q(title__icontains=params.search_keyword))

        if params.subject_id is not None:
            qs = qs.filter(subject_id=params.subject_id)

        prefix = "-" if params.order == "desc" else ""
        return qs.order_by(f"{prefix}{params.sort}")
