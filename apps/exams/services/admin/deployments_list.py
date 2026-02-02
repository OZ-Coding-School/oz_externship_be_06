from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.db.models import Avg, Count, Q, QuerySet
from django.db.models.functions import Coalesce

from apps.exams.constants import ErrorMessages
from apps.exams.models import ExamDeployment


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
        sort_v = sort or cls.DEFAULT_SORT
        order_v = order or cls.DEFAULT_ORDER

        if sort_v not in cls.ALLOWED_SORT or order_v not in cls.ALLOWED_ORDER:
            raise InvalidAdminDeploymentListParams(ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value)

        subject_id_v: int | None = None
        if subject_id:
            try:
                subject_id_v = int(subject_id)
            except ValueError as exc:
                raise InvalidAdminDeploymentListParams(ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value) from exc

        cohort_id_v: int | None = None
        if cohort_id:
            try:
                cohort_id_v = int(cohort_id)
            except ValueError as exc:
                raise InvalidAdminDeploymentListParams(ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value) from exc

        return AdminDeploymentListParams(
            search_keyword=search_keyword or None,
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
