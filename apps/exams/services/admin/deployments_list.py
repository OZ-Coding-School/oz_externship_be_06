from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.db.models import Avg, Count, Q, QuerySet
from django.db.models.functions import Coalesce

from apps.exams.constants import ErrorMessages
from apps.exams.models import ExamDeployment
from apps.exams.validators import normalize_optional_str, parse_optional_positive_int, parse_sort_order


class InvalidAdminDeploymentListParams(Exception):
    """어드민 배포 목록 조회 파라미터가 유효하지 않을 때"""


@dataclass(frozen=True)
class AdminDeploymentListParams:
    search_keyword: Optional[str] = None
    subject_id: Optional[int] = None
    cohort_id: Optional[int] = None
    sort: str = "created_at"
    order: str = "desc"


class AdminDeploymentListService:
    ALLOWED_SORT = {"created_at", "submit_count", "avg_score"}
    ALLOWED_ORDER = {"asc", "desc"}
    DEFAULT_SORT = "created_at"
    DEFAULT_ORDER = "desc"

    @classmethod
    def parse_params(
        cls,
        *,
        search_keyword: str | None,
        subject_id: str | None,
        cohort_id: str | None,
        sort: str | None,
        order: str | None,
    ) -> AdminDeploymentListParams:
        try:
            sort_v, order_v = parse_sort_order(
                sort=sort,
                order=order,
                allowed_sort=cls.ALLOWED_SORT,
                allowed_order=cls.ALLOWED_ORDER,
                default_sort=cls.DEFAULT_SORT,
                default_order=cls.DEFAULT_ORDER,
                error_message=ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST,
            )
            subject_id_v = parse_optional_positive_int(subject_id, ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST)
            cohort_id_v = parse_optional_positive_int(cohort_id, ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST)
            search_keyword_v = normalize_optional_str(
                search_keyword,
                max_length=None,
                error_message=ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST,
            )
        except Exception as exc:
            raise InvalidAdminDeploymentListParams(ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value) from exc

        return AdminDeploymentListParams(
            search_keyword=search_keyword_v,
            subject_id=subject_id_v,
            cohort_id=cohort_id_v,
            sort=sort_v,
            order=order_v,
        )

    @classmethod
    def get_queryset(cls, params: AdminDeploymentListParams) -> QuerySet[ExamDeployment]:
        qs = ExamDeployment.objects.select_related(
            "exam__subject",
            "cohort__course",
        ).annotate(
            submit_count=Count("submissions", distinct=True),
            avg_score=Coalesce(Avg("submissions__score"), 0.0),
        )

        if params.search_keyword:
            qs = qs.filter(Q(exam__title__icontains=params.search_keyword))

        if params.subject_id is not None:
            qs = qs.filter(exam__subject_id=params.subject_id)

        if params.cohort_id is not None:
            qs = qs.filter(cohort_id=params.cohort_id)

        prefix = "-" if params.order == "desc" else ""
        return qs.order_by(f"{prefix}{params.sort}")
