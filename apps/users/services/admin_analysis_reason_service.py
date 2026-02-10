from typing import Any, Dict, List

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.users.models.withdrawal import Withdrawal


class AdminAnalysisReasonService:
    def get_monthly_withdrawal_stats(self, reason: str) -> Dict[str, Any]:
        """탈퇴 사유별 월별 통계 데이터를 집계하여 반환"""
        now = timezone.now()
        # 올해 1월 1일 00:00:00
        from_datetime = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        # 1. 데이터 조회 (QuerySet)
        stats_query = (
            Withdrawal.objects.filter(
                reason=reason,
                created_at__gte=from_datetime,
                created_at__lte=now,
            )
            .annotate(period=TruncMonth("created_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        # 2. 결과 포맷팅
        monthly_items: List[Dict[str, Any]] = [
            {"period": item["period"].strftime("%Y-%m"), "count": item["count"]} for item in stats_query
        ]

        # 3. 추가 정보 계산
        total_count = sum(item["count"] for item in monthly_items)
        reason_label = dict(Withdrawal.Reason.choices).get(reason, "기타")

        return {
            "reason": reason,
            "reason_label": reason_label,
            "from_date": from_datetime.strftime("%Y-%m-%d"),
            "to_date": now.strftime("%Y-%m-%d"),
            "total": total_count,
            "items": monthly_items,
        }
