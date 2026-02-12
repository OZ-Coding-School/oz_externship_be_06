from datetime import date
from typing import Any, TypedDict

from django.db.models import Count, Max, Min, QuerySet
from django.db.models.functions import TruncMonth, TruncYear

from apps.courses.models.cohort_students import CohortStudent
from apps.users.models import User
from apps.users.models.withdrawal import Withdrawal


class TrendItem(TypedDict):
    period: str
    count: int


# 월별/연별 추세 집계 공통 로직
def _aggregate_trends(
    queryset: QuerySet,  # type: ignore[type-arg]
    date_field: str,
    interval: str,
    year: int | None = None,
) -> dict[str, Any]:

    today = date.today()

    if interval == "monthly":
        target_year = year if year else today.year
        from_date = date(target_year, 1, 1)
        to_date = date(target_year, 12, 31)

        qs = (
            queryset.filter(**{f"{date_field}__date__gte": from_date, f"{date_field}__date__lte": to_date})
            .annotate(period=TruncMonth(date_field))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        period_counts: dict[str, int] = {item["period"].strftime("%Y-%m"): item["count"] for item in qs}

        items: list[TrendItem] = [
            {"period": f"{target_year}-{month:02d}", "count": period_counts.get(f"{target_year}-{month:02d}", 0)}
            for month in range(1, 13)
        ]

    else:
        oldest_date = queryset.aggregate(oldest=Min(date_field))["oldest"]
        from_date = date(oldest_date.year, 1, 1) if oldest_date else date(today.year, 1, 1)
        to_date = date(today.year, 12, 31)

        qs = (
            queryset.filter(**{f"{date_field}__date__gte": from_date, f"{date_field}__date__lte": to_date})
            .annotate(period=TruncYear(date_field))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        period_counts = {str(item["period"].year): item["count"] for item in qs}

        items = [
            {"period": str(y), "count": period_counts.get(str(y), 0)} for y in range(from_date.year, today.year + 1)
        ]

    total = sum(item["count"] for item in items)

    return {
        "interval": interval,
        "from_date": from_date,
        "to_date": to_date,
        "total": total,
        "items": items,
    }


def get_signup_trends(interval: str, year: int | None = None) -> dict[str, Any]:
    return _aggregate_trends(User.objects.all(), "created_at", interval, year)


def get_withdrawal_trends(interval: str) -> dict[str, Any]:
    return _aggregate_trends(Withdrawal.objects.all(), "created_at", interval)


def get_student_enrollment_trends(interval: str, year: int | None = None) -> dict[str, Any]:
    return _aggregate_trends(CohortStudent.objects.all(), "created_at", interval, year)


def get_withdrawal_reason_counts() -> dict[str, Any]:
    # count, min, max를 1쿼리로 통합 (기존 3쿼리 → 1쿼리)
    aggregates = Withdrawal.objects.aggregate(
        total=Count("id"),
        oldest=Min("created_at"),
        latest=Max("created_at"),
    )
    total = aggregates["total"]
    from_date = aggregates["oldest"].date() if aggregates["oldest"] else None
    to_date = aggregates["latest"].date() if aggregates["latest"] else None

    qs = Withdrawal.objects.values("reason").annotate(count=Count("id"))

    items = [
        {
            "reason": row["reason"],
            "reason_label": Withdrawal.Reason(row["reason"]).label,
            "count": row["count"],
            "percentage": round((row["count"] / total) * 100, 2) if total else 0.0,
        }
        for row in qs
    ]
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total": total,
        "items": items,
    }
