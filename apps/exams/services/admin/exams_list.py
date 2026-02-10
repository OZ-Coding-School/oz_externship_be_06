from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.db.models import Count, Q, QuerySet

from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam
from apps.exams.validators import (
    normalize_optional_str,
    parse_optional_positive_int,
    parse_sort_order,
)


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
        try:
            sort_v, order_v = parse_sort_order(
                sort=sort,
                order=order,
                allowed_sort=cls.ALLOWED_SORT,
                allowed_order=cls.ALLOWED_ORDER,
                default_sort=cls.DEFAULT_SORT,
                default_order=cls.DEFAULT_ORDER,
                error_message=ErrorMessages.INVALID_EXAM_LIST_REQUEST,
            )
            subject_id_v = parse_optional_positive_int(subject_id, ErrorMessages.INVALID_EXAM_LIST_REQUEST)
            search_keyword_v = normalize_optional_str(
                search_keyword,
                max_length=None,
                error_message=ErrorMessages.INVALID_EXAM_LIST_REQUEST,
            )
        except Exception as exc:
            raise InvalidAdminExamListParams(ErrorMessages.INVALID_EXAM_LIST_REQUEST.value) from exc

        return AdminExamListParams(
            search_keyword=search_keyword_v,
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
