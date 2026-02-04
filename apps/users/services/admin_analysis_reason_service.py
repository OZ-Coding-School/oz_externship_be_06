from typing import Any, Dict, List

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.users.models.withdrawal import Withdrawal


class AdminAnalysisReasonService:
    @staticmethod
    def get_monthly_withdrawal_stats(reason: str) -> Dict[str, Any]:
        now = timezone.now()
        from_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")

        stats_query = (
            Withdrawal.objects.filter(reason=reason)
            .annotate(period=TruncMonth("created_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        items: List[Dict[str, Any]] = [
            {"period": item["period"].strftime("%Y-%m"), "count": item["count"]} for item in stats_query
        ]

        total = sum(item["count"] for item in items)
        reason_label = dict(Withdrawal.Reason.choices).get(reason, "기타")

        return {
            "reason": reason,
            "reason_label": reason_label,
            "from_date": from_date,
            "to_date": to_date,
            "total": total,
            "items": items,
        }
