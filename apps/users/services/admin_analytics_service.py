from datetime import date
from typing import Any, TypedDict

from django.db.models import Count, Min
from django.db.models.functions import TruncMonth, TruncYear

from apps.users.models import User


class TrendItem(TypedDict):
    period: str
    count: int


def get_signup_trends(interval: str, year: int | None = None) -> dict[str, Any]:
    today = date.today()

    if interval == "monthly":
        # 특정 연도의 1~12월
        target_year = year if year else today.year
        from_date = date(target_year, 1, 1)
        to_date = date(target_year, 12, 31)

        # 월별 집계
        queryset = (
            User.objects.filter(
                created_at__date__gte=from_date,
                created_at__date__lte=to_date,
            )
            .annotate(period=TruncMonth("created_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        # 결과를 딕셔너리로 변환
        period_counts: dict[str, int] = {}
        for item in queryset:
            period_str = item["period"].strftime("%Y-%m")
            period_counts[period_str] = item["count"]

        # 1~12월 전체 항목 생성 (데이터 없는 월도 0으로 포함)
        items: list[TrendItem] = []
        for month in range(1, 13):
            period_str = f"{target_year}-{month:02d}"
            items.append({"period": period_str, "count": period_counts.get(period_str, 0)})

    else:
        # yearly - 전체 데이터의 연도별 통계
        # 가장 오래된 가입일 조회
        oldest_date = User.objects.aggregate(oldest=Min("created_at"))["oldest"]

        if oldest_date:
            from_date = date(oldest_date.year, 1, 1)
        else:
            from_date = date(today.year, 1, 1)

        to_date = date(today.year, 12, 31)

        # 년별 집계
        queryset = (
            User.objects.filter(
                created_at__date__gte=from_date,
                created_at__date__lte=to_date,
            )
            .annotate(period=TruncYear("created_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        # 결과를 딕셔너리로 변환
        period_counts = {}
        for item in queryset:
            period_str = str(item["period"].year)
            period_counts[period_str] = item["count"]

        # 가장 오래된 연도부터 현재 연도까지 전체 항목 생성
        items = []
        current_year = from_date.year
        while current_year <= today.year:
            period_str = str(current_year)
            items.append({"period": period_str, "count": period_counts.get(period_str, 0)})
            current_year += 1

    total = sum(item["count"] for item in items)

    return {
        "interval": interval,
        "from_date": from_date,
        "to_date": to_date,
        "total": total,
        "items": items,
    }
